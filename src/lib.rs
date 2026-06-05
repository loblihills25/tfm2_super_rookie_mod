use mod_api::*;
use rand::seq::SliceRandom; // 배열에서 랜덤 추출을 위해 추가
use rand::Rng;
use std::collections::{HashMap, HashSet};

struct SuperRookieMod {
    last_ids: std::sync::Mutex<HashSet<usize>>,
}

impl ModExtension for SuperRookieMod {
    fn post_update(&self, scene: &mut Scene, _ui: &mut GameUI, _assets: &mut Assets, _dt: f32) {
        if let Scene::InGame { data } = scene {
            let mut db = data.db_mut();
            let current_ids: HashSet<usize> = db.athletes.keys().cloned().collect();
            let mut last_ids = self.last_ids.lock().unwrap();

            if !current_ids.is_empty() && *last_ids != current_ids {
                let intersection_count = last_ids.intersection(&current_ids).count();

                if intersection_count < (current_ids.len() * 7 / 10) {
                    // 1. 자유계약(FA) 선수들의 목록을 미리 뽑아 배열(Vec)로 만듭니다.
                    let fa_pool: Vec<_> = db.athletes.values()
                        .filter(|a| {
                            let debug_str = format!("{:?}", a.contract);
                            debug_str.contains("FreeAgent") || debug_str.contains("None")
                        })
                        .cloned()
                        .collect();

                    // 만약 FA 선수가 한 명도 없다면(거의 불가능하지만), 모든 선수 중에서 뽑습니다.
                    let base_pool = if fa_pool.is_empty() {
                        db.athletes.values().cloned().collect::<Vec<_>>()
                    } else {
                        fa_pool
                    };

                    if !base_pool.is_empty() {
                        let mut next_id = current_ids.iter().max().cloned().unwrap_or(0) + 1;
                        let mut rng = rand::thread_rng();

                        for i in 0..100 {
                            // 2. 루프를 돌 때마다 풀에서 무작위로 한 명을 골라 복사합니다.
                            let sample = base_pool.choose(&mut rng).unwrap();
                            let mut rookie = sample.clone();

                            rookie.id = next_id;
                            
                            // 0. 무작위 이름 생성 (4~8글자 프로게이머 닉네임 스타일)
                            let name_length = rng.gen_range(4..=8);
                            let consonants = ['B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'R', 'S', 'T', 'V', 'W', 'X', 'Y', 'Z'];
                            let vowels = ['a', 'e', 'i', 'o', 'u'];
                            let mut random_name = String::new();
                            
                            for char_idx in 0..name_length {
                                if char_idx == 0 {
                                    // 첫 글자는 무조건 대문자 자음
                                    random_name.push(*consonants.choose(&mut rng).unwrap());
                                } else if char_idx % 2 == 1 {
                                    // 짝수 번째(인덱스 1, 3, 5..)는 소문자 모음
                                    random_name.push(*vowels.choose(&mut rng).unwrap());
                                } else {
                                    // 홀수 번째는 소문자 자음
                                    let lower_consonants = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'r', 's', 't', 'v', 'w', 'x', 'y', 'z'];
                                    random_name.push(*lower_consonants.choose(&mut rng).unwrap());
                                }
                            }
                            rookie.name = random_name;
                            
                            rookie.age = rng.gen_range(16..=17);

                            // 1. 전투 능력치 (20~60 랜덤)
                            rookie.stat.last_hit = rng.gen_range(20..=60);
                            rookie.stat.skill_avoid = rng.gen_range(20..=60);
                            rookie.stat.skill_hit = rng.gen_range(20..=60);
                            rookie.stat.control_speed = rng.gen_range(20..=60);
                            rookie.stat.positioning = rng.gen_range(20..=60);

                            // 2. 정신력 능력치 (20~60 랜덤)
                            rookie.stat.judgement = rng.gen_range(20..=60);
                            rookie.stat.mental = rng.gen_range(20..=60);
                            rookie.stat.concentration = rng.gen_range(20..=60);

                            // 3. 성향 4종 (70~100 랜덤)
                            rookie.stat.ego = rng.gen_range(70..=100);
                            rookie.stat.order = rng.gen_range(70..=100);
                            rookie.stat.roaming = rng.gen_range(70..=100);
                            rookie.stat.aggressive = rng.gen_range(70..=100);

                            // 4. 주 포지션 100, 부 포지션 50 설정
                            rookie.stat.top = 0;
                            rookie.stat.jungle = 0;
                            rookie.stat.mid = 0;
                            rookie.stat.bottom = 0;
                            rookie.stat.support = 0;

                            let mut positions = vec![0, 1, 2, 3, 4];
                            positions.shuffle(&mut rng); // 포지션 섞기

                            let main_pos = positions[0];
                            let sub_pos = positions[1];

                            // 포지션 점수 할당 클로저 (usize 타입 적용)
                            let mut assign_pos = |pos_idx: i32, score: usize| match pos_idx {
                                0 => rookie.stat.top = score,
                                1 => rookie.stat.jungle = score,
                                2 => rookie.stat.mid = score,
                                3 => rookie.stat.bottom = score,
                                _ => rookie.stat.support = score,
                            };

                            assign_pos(main_pos, 100); // 주 포지션 100
                            assign_pos(sub_pos, 50);   // 부 포지션 50

                            // 5. 언어 설정 (정확히 50명은 한국어, 50명은 샘플 기본 언어)
                            // i가 0~49일 때(50명)는 무조건 한국어 부여
                            if i < 50 {
                                let mut lang_map = HashMap::new();
                                lang_map.insert(0, 100); // 0번이 한국어, 수치 100이 게임상 5점 만점
                                rookie.stat.language = lang_map;
                            } else {
                                // 나머지 50명은 기존 sample의 언어를 그대로 유지 (글로벌 용병)
                            }

                            // 6. 세밀한 히든 스탯 및 관리 수치 설정
                            rookie.hidden.potential = rng.gen_range(90..=100);
                            
                            rookie.hidden.stamina_recovery_min = 30;
                            rookie.hidden.stamina_recovery_max = 50;
                            
                            rookie.hidden.stamina_cost_per_set_min = rng.gen_range(10..=20);
                            rookie.hidden.stamina_cost_per_set_max = rng.gen_range(30..=40);
                            
                            rookie.hidden.stress_sensitivity = rng.gen_range(0..=30);
                            
                            rookie.hidden.condition_baseline = rng.gen_range(80..=100);
                            rookie.hidden.condition_amplitude = rng.gen_range(0..=30);
                            rookie.hidden.condition_period = rng.gen_range(10..=30);
                            rookie.hidden.condition_phase = rng.gen_range(0..=30);
                            
                            rookie.hidden.match_impact_sensitivity = rng.gen_range(0..=100);

                            // 7. 팬 수 설정 (management 구조체)
                            rookie.management.fan_count = rng.gen_range(500..=2000);

                            db.athletes.insert(next_id, rookie);
                            next_id += 1;
                        }
                        println!(">>> Super Rookie Mod: 100 FA Rookies Injected (50% KR, Main Pos 100, Sub Pos 50)!");
                    }
                }
                *last_ids = db.athletes.keys().cloned().collect();
            }
        }
    }
}

fn init(_ctx: &GameCtx) -> ModRegistration {
    let mut reg = ModRegistration::new("super_rookie_mod");
    reg.set_extension(SuperRookieMod {
        last_ids: std::sync::Mutex::new(HashSet::new()),
    });
    reg
}

declare_mod!(init);
