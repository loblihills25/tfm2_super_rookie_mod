# Teamfight Manager 2 - Super Rookie Mod

DB 무작위 재생성 시 100명의 고성능 슈퍼 루키(자유계약 신분)를 즉시 추가하는 모드입니다.

## Features
- **100 Unique Rookies**: 이름과 전투 수치가 모두 다른 100명의 유망주가 생성됩니다.
- **High Potential**: 잠재력 90~100 사이.
- **Age**: 16~17세.
- **Mental Stats**: 판단력(Judgement), 집중력(Concentration), 정신력(Mental) 등 모든 정신적 스탯이 높게 부여됩니다.
- **Traits**: 에고(Ego), 오더(Order), 로밍(Roaming), 공격성(Aggressive) 수치가 70 이상으로 보장됩니다.
- **Positions**: 주 포지션 숙련도 100, 부 포지션 50으로 랜덤 배분됩니다.
- **Language**: 신인 중 정확히 50명은 한국어(Korean) 숙련도 100을 가지며, 나머지는 글로벌 용병 설정을 유지합니다.
- **Free Agent**: 100명 모두 이적료와 연봉이 없는 완전한 FA 상태로 생성됩니다.

---

## 🛠️ Modding Resources: Discovered Internal Field Names
TFM2 모딩을 하시는 분들을 위해, 컴파일러 에러 유도 및 로그 추출을 통해 알아낸 `Athlete` 내부 구조체의 실제 필드명(Variable Names)을 공유합니다.

### 1. `AthleteStat` (전투 및 정신력 스탯)
* `last_hit` (몬스터처치)
* `skill_avoid` (스킬회피)
* `skill_hit` (스킬적중)
* `positioning` (포지셔닝)
* `control_speed` (컨트롤속도)
* `judgement` (판단력) - *주의: judgment가 아님*
* `mental` (정신력)
* `concentration` (집중력) - *주의: focus가 아님*
* `top`, `jungle`, `mid`, `bottom`, `support` (포지션 숙련도: 0~100)
* `language` (언어 숙련도 Map: `HashMap<u32, u8>`)

### 2. `AthleteStat` (성향 관련 - Hidden이 아님!)
에고, 공격성 등의 성향 스탯은 `hidden` 구조체가 아니라 `stat` 구조체 내부에 존재합니다.
* `ego` (에고)
* `order` (오더)
* `roaming` (로밍)
* `aggressive` (공격성) - *주의: aggression이 아님*

### 3. `AthleteHiddenStat` (히든 및 신체 스탯)
* `potential` (잠재력)
* `stamina_recovery_min` / `stamina_recovery_max` (체력 회복)
* `stamina_cost_per_set_min` / `stamina_cost_per_set_max` (세트당 체력 소모)
* `stress_sensitivity` (스트레스 민감도)
* `condition_baseline` / `condition_amplitude` / `condition_period` / `condition_phase` (컨디션 관련)
* `match_impact_sensitivity` (경기 결과 민감도)

### 4. 기타 주요 필드
* `age`: 나이 (Athlete 본체)
* `management.fan_count`: 팬 수
* `contract.salary`: 연봉 (계약 상태일 경우)
* `contract.transfer_fee`: 이적료 (계약 상태일 경우)
* **FA(무소속) 판별법**: `contract` 데이터 내부가 `FreeAgent` 상태거나 `team_id`가 존재하지 않는 형태로 저장됨. (본 모드에서는 기존 FA 선수를 `clone()`하여 이 문제를 안전하게 우회했습니다.)

---

## How to Build
1. Require Rust Toolchain (nightly-2026-06-04 recommended).
2. Run via TFM2ModUploader.exe or manual `cargo build --release`.
3. Copy `super_rookie_mod.dll` and `mod.mod_info` to `mods/super_rookie_mod/`.