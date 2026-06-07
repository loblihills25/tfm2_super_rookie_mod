#!/usr/bin/env python3
"""
super_rookie_fa_buffer.py
=========================

TFM2 (.tfm2db) "Super Rookie" tool, built on top of the field-notes
template-roundtrip pair:

    tfm2db_to_csv.py   (export, read-only)
    csv_to_tfm2db.py   (conservative in-place importer)

------------------------------------------------------------------------------
READ THIS FIRST — what this tool does and does NOT do
------------------------------------------------------------------------------
`csv_to_tfm2db.py` is a CONSERVATIVE in-place editor. It only rewrites
fixed-width fields of records that already exist, matched by id against the
original export. It cannot:

    * add brand-new athletes (new ids in the CSV are silently skipped),
    * change a player's NAME (length-changing strings are unsupported).

So this tool does NOT spawn 100 new players. Instead it BUFFS up to 100
EXISTING free agents (FA) in place to the requested super-rookie profile.
This is the part that actually persists across save/load with these tools and
carries no save-corruption risk (no records added, no byte sizes changed).

Limitations carried over from the importer:
    * Names are left unchanged (random names are not possible in place).
    * "Korean = 100" only takes effect on FAs that ALREADY have a Korean
      language slot; the importer cannot add a new language slot.
    * Existing FAs already have no salary / transfer fee, so the "pure FA"
      requirement is satisfied automatically.

------------------------------------------------------------------------------
SAFETY
------------------------------------------------------------------------------
This tool NEVER writes over the input file. It writes a new output file and
leaves CSVs next to it for inspection. Still: back up your save first.

------------------------------------------------------------------------------
REQUIREMENTS
------------------------------------------------------------------------------
Place these three files in the SAME folder:
    super_rookie_fa_buffer.py   (this file)
    tfm2db_to_csv.py
    csv_to_tfm2db.py

Run (GUI):      double-click the exe, or `python super_rookie_fa_buffer.py`
Run (CLI):      python super_rookie_fa_buffer.py INPUT.tfm2db [OUTPUT.tfm2db]

Build exe:      pyinstaller --onefile --noconsole super_rookie_fa_buffer.py
                (pyinstaller follows the imports and bundles the two modules
                 as long as they sit next to this file)
"""

from __future__ import annotations

import csv
import random
import sys
import traceback
from pathlib import Path
from typing import Callable

# The two field-notes modules must be importable (same folder).
import tfm2db_to_csv as exp
import csv_to_tfm2db as imp

# ---------------------------------------------------------------------------
# Spec: column groups (names exactly match tfm2db_to_csv export columns)
# ---------------------------------------------------------------------------

# 20-60 combat & mental (spec "last_hit" == export "ability_unit_kill")
COMBAT_MENTAL_COLUMNS = [
    "ability_unit_kill",
    "ability_skill_avoid",
    "ability_skill_hit",
    "ability_control_speed",
    "ability_positioning",
    "ability_judgement",
    "ability_mental",
    "ability_concentration",
]

# 70-100 persona
PERSONA_COLUMNS = [
    "ability_order",
    "ability_roaming",
    "ability_aggressive",
    "ability_ego",
]

ROLE_COLUMNS = [
    "role_top",
    "role_jungle",
    "role_mid",
    "role_bottom",
    "role_support",
]


def _set(row: dict, column: str, value) -> None:
    """Set a CSV cell as a string (the importer parses strings)."""
    row[column] = str(value)


def buff_fa_row(row: dict, make_korean: bool) -> None:
    """Apply the super-rookie profile to one existing FA row, in place.

    Only stat columns are touched. player_id and all *_offset / *_index
    columns are left untouched so the importer can locate the record.
    """
    # Age 16-17
    _set(row, "age", random.randint(16, 17))

    # Combat & mental 20-60
    for col in COMBAT_MENTAL_COLUMNS:
        _set(row, col, random.randint(20, 60))

    # Persona 70-100
    for col in PERSONA_COLUMNS:
        _set(row, col, random.randint(70, 100))

    # Positions: one main (100), one sub (50), rest 0
    main_idx, sub_idx = random.sample(range(5), 2)
    for i, col in enumerate(ROLE_COLUMNS):
        if i == main_idx:
            _set(row, col, 100)
        elif i == sub_idx:
            _set(row, col, 50)
        else:
            _set(row, col, 0)

    # Hidden / potential block
    _set(row, "potential_base", random.randint(90, 100))
    _set(row, "potential_stamina_recovery_min", 30)
    _set(row, "potential_stamina_recovery_max", 50)
    _set(row, "potential_stamina_cost_per_set_min", random.randint(10, 20))
    _set(row, "potential_stamina_cost_per_set_max", random.randint(30, 40))
    _set(row, "potential_stress_sensitivity", random.randint(0, 30))
    _set(row, "potential_condition_baseline", random.randint(80, 100))
    _set(row, "potential_condition_amplitude", random.randint(0, 30))
    _set(row, "potential_condition_period", random.randint(10, 30))
    _set(row, "potential_condition_phase", random.randint(0, 30))
    _set(row, "potential_match_result_sensitivity", random.randint(0, 100))

    # Fans 500-2000
    _set(row, "fans", random.randint(500, 2000))

    # Language: half get Korean=100 (only takes effect if a Korean slot
    # already exists for that FA). The other half keep their original setting.
    if make_korean:
        _set(row, "language_korea", 100)

    # Pure-FA contract: existing FAs already have no salary/fee. Setting these
    # to 0 is a safe no-op when there is no salary offset (importer skips it).
    if str(row.get("salary_offset", "")).strip():
        _set(row, "weekly_salary_raw_krw", 0)
    if str(row.get("transfer_value_offset_guess", "")).strip():
        _set(row, "transfer_value_raw_krw_guess", 0)


def is_free_agent(row: dict) -> bool:
    in_team = str(row.get("in_team", "")).strip()
    return in_team in ("", "0")


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def run_pipeline(
    input_path: Path,
    output_path: Path,
    count: int | None = None,
    log: Callable[[str], None] = print,
) -> tuple[int, int]:
    """tfm2db -> CSV -> buff FAs -> tfm2db.

    `count` = None  -> buff ALL free agents (default).
    `count` = N     -> buff only the first N free agents (by player_id).

    Returns (fa_buffed, fields_changed).
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    if input_path.resolve() == output_path.resolve():
        raise ValueError("Output path must differ from input (never overwrite the original db file).")

    work_dir = output_path.parent / f"{output_path.stem}_csv"
    orig_dir = work_dir / "original"
    edited_dir = work_dir / "edited"
    orig_dir.mkdir(parents=True, exist_ok=True)
    edited_dir.mkdir(parents=True, exist_ok=True)

    # --- 1. tfm2db -> CSV (using the field-notes exporter) -----------------
    log(f"Reading and decompressing: {input_path.name}")
    data = exp.read_payload(input_path)
    teams = exp.parse_teams(data)
    teams_by_id = {t.team_id: t for t in teams}
    players = exp.parse_players(data, teams_by_id)
    coaches = exp.parse_coaches(data, teams_by_id)
    log(f"Decoded {len(players)} players, {len(teams)} teams, {len(coaches)} coaches.")

    exp.export_players(players, orig_dir / "players.csv")
    exp.export_teams(data, teams, orig_dir / "teams.csv")
    exp.export_coaches(coaches, orig_dir / "coaches.csv")
    log(f"Original CSVs written to: {orig_dir}")

    # --- 2. Build the edited players.csv (buff FAs in place) ---------------
    with (orig_dir / "players.csv").open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    fa_rows = [r for r in rows if is_free_agent(r)]
    log(f"Found {len(fa_rows)} free agents in the database.")
    if not fa_rows:
        raise ValueError("No free agents found to buff. Nothing to do.")

    selected = fa_rows if count is None else fa_rows[: max(0, count)]
    korean_half = len(selected) // 2  # first half get Korean=100
    for i, row in enumerate(selected):
        buff_fa_row(row, make_korean=(i < korean_half))
    log(f"Buffed {len(selected)} free agents "
        f"({korean_half} set to Korean, {len(selected) - korean_half} keep original language).")

    with (edited_dir / "players.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    log(f"Edited CSV written to: {edited_dir / 'players.csv'}")

    # --- 3. CSV -> tfm2db (in-place patch via the field-notes importer) ----
    log("Patching .tfm2db file (in-place, fixed-width fields only)...")
    original_raw, gz_off, payload_bytes = imp.read_wrapper(input_path)
    payload = bytearray(payload_bytes)
    changes = imp.patch_players(
        payload,
        imp.read_csv(orig_dir / "players.csv"),
        imp.read_csv(edited_dir / "players.csv"),
    )
    imp.write_wrapper(original_raw, gz_off, bytes(payload), output_path)
    log(f"Applied {len(changes)} field changes.")
    log(f"DONE. New .tfm2db written to: {output_path}")
    return len(selected), len(changes)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def default_output(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}_super_rookie{input_path.suffix}")


def run_cli(argv: list[str]) -> int:
    if not argv:
        return -1  # signal "no args -> try GUI"
    in_path = Path(argv[0])
    out_path = Path(argv[1]) if len(argv) > 1 else default_output(in_path)
    try:
        buffed, changed = run_pipeline(in_path, out_path, log=print)
        print(f"\nSUCCESS: buffed {buffed} FAs, {changed} field changes -> {out_path}")
        return 0
    except Exception as exc:  # noqa: BLE001
        traceback.print_exc()
        print(f"\nFAILED: {exc}")
        return 1


# ---------------------------------------------------------------------------
# Minimal GUI (for the double-click / pyinstaller exe use case)
# ---------------------------------------------------------------------------

def run_gui() -> int:
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext, ttk

    root = tk.Tk()
    root.title("TFM2 Super Rookie - FA Buffer")
    root.geometry("680x520")

    frame = ttk.Frame(root, padding=12)
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frame, text="TFM2 Super Rookie (FA in-place buffer)",
              font=("Arial", 13, "bold")).pack(anchor="w")
    ttk.Label(frame,
              text="Buffs up to 100 existing Free Agents. Writes a NEW file; "
                   "your original .tfm2db is never modified.").pack(anchor="w", pady=(0, 8))

    state = {"input": None}
    log_area = scrolledtext.ScrolledText(frame, height=20, font=("Consolas", 9))

    def log(msg: str) -> None:
        log_area.insert(tk.END, msg + "\n")
        log_area.see(tk.END)
        root.update_idletasks()

    def choose_and_run() -> None:
        path = filedialog.askopenfilename(
            title="Select TFM2 .tfm2db file",
            filetypes=[("TFM2 .tfm2db Files", "*.tfm2db"), ("All files", "*.*")],
        )
        if not path:
            return
        in_path = Path(path)
        out_path = filedialog.asksaveasfilename(
            title="Save patched file as",
            defaultextension=".tfm2db",
            initialfile=default_output(in_path).name,
            filetypes=[("TFM2 .tfm2db Files", "*.tfm2db")],
        )
        if not out_path:
            return
        log_area.delete("1.0", tk.END)
        try:
            buffed, changed = run_pipeline(in_path, Path(out_path), log=log)
            messagebox.showinfo("Success",
                                f"Buffed {buffed} free agents.\n{changed} field changes.\n\n"
                                f"Saved to:\n{out_path}")
        except Exception as exc:  # noqa: BLE001
            log(traceback.format_exc())
            messagebox.showerror("Error", f"Patching failed:\n\n{exc}")

    ttk.Button(frame, text="Select .tfm2db file and buff FAs...",
               command=choose_and_run).pack(fill=tk.X, pady=6)
    log_area.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

    root.mainloop()
    return 0


def main() -> int:
    code = run_cli(sys.argv[1:])
    if code == -1:
        try:
            return run_gui()
        except Exception:  # noqa: BLE001 - headless environment, no Tk
            print("Usage: super_rookie_fa_buffer.py INPUT.tfm2db [OUTPUT.tfm2db]")
            return 2
    return code


if __name__ == "__main__":
    raise SystemExit(main())
