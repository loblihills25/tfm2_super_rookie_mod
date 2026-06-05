# Teamfight Manager 2 - Super Rookie Mod (v1.1.0)

데이터베이스 수정 화면에서 '무작위 재생성'을 실행할 때, 지정된 스탯 범위를 가진 100명의 유망주를 추가로 생성하는 Native Rust Mod입니다.

## Mod Features

* **생성 인원**: 100명 (이름 랜덤 조합 생성)
* **나이**: 16 ~ 17세 고정
* **포지션 숙련도**: 1개 포지션 숙련도 100, 다른 1개 포지션 숙련도 50, 나머지 0 (랜덤 배분)
* **전투 및 정신력 스탯**: 20 ~ 60 사이 랜덤 부여
  * `last_hit`, `skill_avoid`, `skill_hit`, `control_speed`, `positioning`
  * `judgement`, `mental`, `concentration`
* **성향 스탯**: 70 ~ 100 사이 랜덤 부여
  * `ego`, `order`, `roaming`, `aggressive`
* **히든 스탯**: 
  * `potential`: 90 ~ 100 랜덤
  * `stamina_recovery_min` (30), `stamina_recovery_max` (50) 고정
  * `stamina_cost_per_set_min` (10~20), `stamina_cost_per_set_max` (30~40) 랜덤
  * `stress_sensitivity` (0~30), `condition_amplitude` (0~30), `condition_phase` (0~30) 랜덤
  * `condition_baseline` (80~100), `condition_period` (10~30) 랜덤
  * `match_impact_sensitivity` (0~100) 랜덤
* **관리 스탯**: 팬 수 500 ~ 2000 사이 랜덤
* **언어 설정**: 50명은 한국어 숙련도 100으로 생성, 나머지 50명은 원본 FA 선수의 언어 설정 유지
* **계약 상태**: 100명 모두 이적료(Transfer Fee)와 연봉(Salary)이 없는 완전 FA 상태로 생성

---

## Modding Resources: Discovered Internal Field Names
본 모드 제작 중 확인된 `Athlete` 내부 구조체의 실제 필드명입니다.

### 1. `AthleteStat` (전투 및 정신력 스탯)
* `last_hit`, `skill_avoid`, `skill_hit`, `positioning`, `control_speed`
* `judgement`, `mental`, `concentration`
* `top`, `jungle`, `mid`, `bottom`, `support`
* `language` (`HashMap<u32, u8>`)

### 2. `AthleteStat` (성향 관련)
* `ego`, `order`, `roaming`, `aggressive`

### 3. `AthleteHiddenStat` (히든 및 신체 스탯)
* `potential`
* `stamina_recovery_min`, `stamina_recovery_max`
* `stamina_cost_per_set_min`, `stamina_cost_per_set_max`
* `stress_sensitivity`
* `condition_baseline`, `condition_amplitude`, `condition_period`, `condition_phase`
* `match_impact_sensitivity`

### 4. 기타 주요 필드
* `age` (Athlete 본체)
* `management.fan_count` (AthleteManagementStat 내부)
* `contract.salary` (InContract 내부)
* `contract.transfer_fee` (InContract 내부)
