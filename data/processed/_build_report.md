# 빌드 리포트

base 시즌: 2026 (파일명 2025는 오기)


## 풀
Pos∈['FW'], 90s≥5 → **22명**


## 2026 스탯 파일
  - 동명이인 `Gun-Hee Kim` 2줄 → Kim Gun-hee: 골/도움 대조로 선택
- ✅ `kleague1_2026_xa_player_stats.md` → 풀 매칭 21/22명, 지표 ['assists_src', 'xa']
  - 동명이인 `Gun-Hee Kim` 2줄 → Kim Gun-hee: ⚠ 특정 불가, 이 파일 스킵
- ✅ `kleague1_2026_chances_created_stats.md` → 풀 매칭 21/22명, 지표 ['key_passes', 'key_passes_90']
  - 동명이인 `Gun-Hee Kim` 2줄 → Kim Gun-hee: 골/도움 대조로 선택
- ✅ `kleague1_2026_big_chances_created_stats.md` → 풀 매칭 17/22명, 지표 ['big_chances_created']
- ✅ `kleague1_2026_big_chances_missed_stats.md` → 풀 매칭 20/22명, 지표 ['big_chances_missed', 'shot_conversion_pct']
  - 동명이인 `Gun-Hee Kim` 2줄 → Kim Gun-hee: ⚠ 특정 불가, 이 파일 스킵
- ✅ `kleague1_2026_shots_on_target_per90_stats.md` → 풀 매칭 20/22명, 지표 ['sot_90_src', 'shot_accuracy_pct']
- ✅ `kleague1_2026_dribbles_completed_per90_stats.md` → 풀 매칭 18/22명, 지표 ['dribbles_90', 'dribble_success_pct']
- ✅ `kleague1_2026_penalties_won_fouls_drawn_stats.md` → 풀 매칭 7/22명, 지표 ['pk_won', 'fouls_drawn_90']
  - 동명이인 `Gun-Hee Kim` 2줄 → Kim Gun-hee: 골/도움 대조로 선택
- ✅ `kleague1_2026_xg_player_stats.md` → 풀 매칭 21/22명, 지표 ['goals_src', 'xg']
- ✅ `xg.csv` (부분 발췌) → 지표 ['xg']

### 교차검증 (base CSV vs FotMob 파일)
- 도움: 전부 ±1 이내 ✅
- 골: 전부 ±1 이내 ✅

### bio.csv
- 채워진 선수: 22/22

→ `data/processed/strikers_2026.csv` (22행)

### 2026 지표별 결측
- **xg**: 21/22 — 결측: Kong Minhyu
- **xa**: 21/22 — 결측: Kong Minhyu
- **key_passes_90**: 21/22 — 결측: Kong Minhyu
- **dribbles_90**: 21/22 — 결측: Kong Minhyu
- **big_chances_created**: 21/22 — 결측: Kong Minhyu
- **big_chances_missed**: 21/22 — 결측: Kong Minhyu
- **fouls_drawn_90**: 7/22 — 결측: Abdallah Hleihil, Tiago Orobó, Patryk Klimala, Breno Herculano, Vitor Gabriel, Joo Min-kyu, Kim Sinjin, Jeong Jaemin, Lee Kunhee, Kong Minhyu, Bruno Mota, Hólmbert Friðjónsson, Choe Byeongchan, Kim Gun-hee, Lee Sang-heon
- **shot_accuracy_pct**: 19/22 — 결측: Jhon Montaño, Kong Minhyu, Kim Gun-hee

## 2025 스탯 파일 (직전 시즌)
- ✅ `kleague1_2025_xg_player_stats.md` → 풀 매칭 14/22명, 지표 ['goals', 'xg']
- ✅ `kleague1_2025_xa_player_stats.md` → 풀 매칭 14/22명, 지표 ['assists', 'xa']
- ✅ `kleague1_2025_chances_created_stats.md` → 풀 매칭 12/22명, 지표 ['key_passes', 'key_passes_90']
- ✅ `kleague1_2025_minutes_played_stats.md` → 풀 매칭 14/22명, 지표 ['matches', 'minutes']
- ✅ `kleague1_2025_shots_on_target_per90_stats.md` → 풀 매칭 7/22명, 지표 ['sot_90', 'shot_accuracy_pct']
- ✅ `kleague1_2025_dribbles_completed_per90_stats.md` → 풀 매칭 7/22명, 지표 ['dribbles_90', 'dribble_success_pct']

→ `data/processed/strikers_2025.csv` — 2025 기록 있는 풀 선수 **14명**
  (Bruno Mota, Choe Byeongchan, Hólmbert Friðjónsson, Joo Min-kyu, Kim Gun-hee, Kim Sinjin, Lee Hojae, Lee Kunhee, Lee Sang-heon, Marcão, Patryk Klimala, Tiago Orobó, Vitor Gabriel, Yago Cariello)

### 2025 지표별 커버
- **minutes**: 14/14
- **matches**: 14/14
- **goals**: 14/14
- **assists**: 14/14
- **xg**: 14/14
- **xa**: 14/14
- **key_passes_90**: 12/14
- **sot_90**: 7/14
- **dribbles_90**: 7/14