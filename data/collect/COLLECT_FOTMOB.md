# 데이터 수집 & 재빌드 (옵션 B)

FotMob 리그 리더보드를 markdown 표로 저장 → `python rebuild.py` → 대시보드 갱신.
자동 스크래핑 안 함(FBref 봇차단 / kleague.com robots.txt / FotMob ToS 금지). 수동 복사만.

## 워크플로

1. FotMob → K League 1 → 통계 탭 → 지표 선택 → "더 보기" 끝까지 → 표 복사
2. `2026 Stats/` 또는 `2025 Stats/` 에 `.md` 로 저장 (기존 파일과 같은 markdown 표 형식)
3. 새 지표면 `src/statfiles.py` 의 `STAT_FILES` 에 `{원본 컬럼명: 정규 지표명}` 한 줄 추가
4. `python rebuild.py` → `data/processed/` 갱신 + `_build_report.md` 에 매칭/결측 리포트
5. `./run.sh`

표 형식 (기존 파일 그대로): `| 순위 | 선수명 | 지표1 | 지표2 | ... | 평가 |`
선수명은 FotMob 로마자(예: "Dong-Gyeong Lee"). 매칭 안 되는 새 이름은 `data/name_map.csv` 에 추가.

## 수집 현황 (FW 스트라이커 22명 풀)

### 2026 시즌 (base CSV 와 같은 시즌)
| 지표 | 파일 | 상태 |
|---|---|---|
| 골·도움·슈팅·유효슈팅·유효슈팅%·90s | (base CSV) | ✅ |
| xA | `2026 Stats/kleague1_2026_xa_player_stats.md` | ✅ 21/22 |
| 기회 창출(키패스) | `..._chances_created_stats.md` | ✅ 21/22 |
| 빅찬스 창출 | `..._big_chances_created_stats.md` | ✅ 21/22 |
| 빅찬스 놓침 + 슈팅전환율 | `..._big_chances_missed_stats.md` | ✅ 21/22 |
| 유효슈팅/90 + 정확도 | `..._shots_on_target_per90_stats.md` | ✅ 20/22 |
| 드리블 성공/90 + 성공률 | `..._dribbles_completed_per90_stats.md` | ✅ 21/22 |
| xG (전체) | — | ⚠ **부분 17/22** (`fotmob_2026/xg.csv`). **전체 파일 필요** |
| 피파울/90 | `..._penalties_won_fouls_drawn_stats.md` | 🟡 PK 획득자 7/22만 (전체 피파울 리더보드 있으면 교체) |

### 2025 시즌 (직전 시즌 레이어 — "두 시즌 다 뛴 선수"에만 적용)
| 지표 | 상태 |
|---|---|
| xG + 골 | ✅ `2025 Stats/kleague1_2025_xg_player_stats.md` |
| 드리블 성공/90 | ✅ |
| **도움 / xA** | ❌ (xA 리더보드 받으면 도움 포함) |
| **기회 창출** | ❌ |
| **유효슈팅 / 정확도** | ❌ |
| **출전 (경기수·분)** | ❌ ← per-90·풀필터에 필수 |

## 다음에 받을 것 (우선순위)

1. **2026 xG 전체 리더보드** (지금 17/22 → 22/22)
2. **2025: xA · 기회창출 · 유효슈팅 · 출전(Minutes/Appearances)**
3. (옵션) 2026 전체 피파울 리더보드

## 그 외 (FotMob 아님, 수동)
- `bio.csv` — Transfermarkt (생년월일·키·주발·대표팀·시장가치·계약)
- `brand_marketing.csv` — 인스타(참여율·팔로워)·네이버뉴스(노출건수)
