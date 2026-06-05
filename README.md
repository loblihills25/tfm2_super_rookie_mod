# Teamfight Manager 2 - Super Rookie Mod (v1.1.0)

Teamfight Manager 2(팀파이트 매니저 2)의 데이터베이스 수정 화면에서 **'무작위 재생성'** 기능을 사용할 때, 게임의 흐름을 바꿀 수 있는 **100명의 고성능 슈퍼 루키(S급 유망주)**를 즉시 추가해 주는 Native Rust Mod입니다. 

단순히 능력치만 높은 복제 선수가 아닌, 각기 다른 외모와 랜덤화된 세부 능력치를 가진 "고유한(Unique)" 유망주들이 생성되어 스토브리그와 영입 시장에 활력을 불어넣습니다.

## 🌟 Mod Features (상세 기능)

* **100 Unique Rookies (100인 100색 유망주)**
  * 기존 FA 선수들의 외모 데이터를 무작위로 차용하고 4~8글자 사이의 영문 닉네임(e.g., Zato, Kirel)을 절묘하게 조합하여, 100명의 선수가 모두 다른 이름과 외모를 갖도록 생성됩니다.
* **Golden Age (황금 세대)**
  * 생성되는 모든 선수의 나이는 영입하기 가장 좋은 **16세에서 17세**로 고정됩니다.
* **High Potential & Hidden Stats (압도적 잠재력)**
  * 모든 루키의 잠재력(Potential)은 **90~100** 사이로 부여되어, 어떤 팀에 가더라도 에이스로 성장할 수 있습니다.
  * 체력 회복력, 세트당 체력 소모, 컨디션 유지력 등 숨겨진 관리 스탯들도 최상급으로 세팅됩니다.
* **Aggressive & Smart (공격적이고 똑똑한 플레이)**
  * 에고(Ego), 오더(Order), 로밍(Roaming), 공격성(Aggressive) 수치가 무조건 **70 이상**으로 부여되어, 게임 내에서 매우 주도적이고 공격적인 플레이 메이킹을 보여줍니다.
* **Specialized Positions (명확한 주 포지션)**
  * 5개의 포지션 중 하나가 무작위로 '주 포지션(숙련도 100)'으로 설정되며, 다른 하나는 '부 포지션(숙련도 50)'으로 설정됩니다. 나머지 포지션은 0으로 고정되어 확실한 롤을 부여받습니다.
* **Bilingual Talent (한국어 및 글로벌 최적화)**
  * 생성되는 100명 중 정확히 **50명은 한국어(Korean) 숙련도 만점**을 가지며, 나머지 50명은 다양한 글로벌 언어 설정을 유지하여 다국적 로스터 구성에 재미를 더합니다.
* **Ready for Transfer (완벽한 FA 신분)**
  * 생성된 루키들은 모두 특정 팀에 소속되지 않은 상태이며, 이적료(Transfer Fee)와 기존 연봉(Salary)이 없는 100% 완전한 자유계약(FA) 신분으로 영입 시장에 등장합니다.

---

## 🛠️ Modding Resources: Discovered Internal Field Names
본 모드를 제작하며 확인된 TFM2 `Athlete` 구조체의 실제 내부 변수명(Variable Names)을 다른 모더들을 위해 공유합니다. 모드 제작 시 참고하시기 바랍니다.

### 1. `AthleteStat` (전투 및 정신력 스탯)
* `last_hit` (몬스터처치)
* `skill_avoid` (스킬회피)
* `skill_hit` (스킬적중)
* `positioning` (포지셔닝)
* `control_speed` (컨트롤속도)
* `judgement` (판단력)
* `mental` (정신력)
* `concentration` (집중력)
* `top`, `jungle`, `mid`, `bottom`, `support` (포지션 숙련도: 0~100)
* `language` (언어 숙련도 Map: `HashMap<u32, u8>`)

### 2. `AthleteStat` (성향 관련)
에고, 공격성 등의 성향 스탯은 `hidden`이 아니라 `stat` 구조체 내부에 존재합니다.
* `ego` (에고)
* `order` (오더)
* `roaming` (로밍)
* `aggressive` (공격성)

### 3. `AthleteHiddenStat` (히든 및 신체 스탯)
* `potential` (잠재력)
* `stamina_recovery_min` / `stamina_recovery_max` (체력 회복)
* `stamina_cost_per_set_min` / `stamina_cost_per_set_max` (세트당 체력 소모)
* `stress_sensitivity` (스트레스 민감도)
* `condition_baseline` / `condition_amplitude` / `condition_period` / `condition_phase` (컨디션 관련)
* `match_impact_sensitivity` (경기 결과 민감도)

### 4. 기타 주요 필드
* `age`: 나이 (Athlete 본체)
* `management.fan_count`: 팬 수 (AthleteManagementStat 내부)
* `contract.salary`: 연봉 (InContract 내부)
* `contract.transfer_fee`: 이적료 (InContract 내부)