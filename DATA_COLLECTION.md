# 데이터 수집 가이드

> **2026-08-28 업데이트**: 경기력 스탯은 **FotMob 리그 리더보드**(지표별 1페이지)로 수집하는
> 방식으로 변경. 상세는 **[`data/collect/COLLECT_FOTMOB.md`](data/collect/COLLECT_FOTMOB.md)** 참고.
> 아래 "1. advanced_stats" 섹션의 선수별 페이지 방식은 폐기. `bio.csv` / `brand_marketing.csv` /
> `history.csv` 는 그대로 유효.

목표: 현재 "슈팅·득점 계열 7개 지표"만 있는 파일럿을, **스트라이커 포지션 특화 + 창출·전진·성장세·마케팅**까지
갖춘 포트폴리오로 끌어올린다.

## 확정된 범위

- **포지션**: 스트라이커만 (`Pos == "FW"`, 22명). percentile 은 이 22명 풀 내부에서 재계산.
  - 22명이 얇게 느껴지면 `FWMF`(15명, 스트라이커 겸업)를 합쳐 37명 풀로 갈 수도 있음 → 수집 후 판단.
- **시즌**: **2025 완료 시즌 = Current Ability 기준 / 2026 현재 시즌 = 현재 폼·성장세 레이어** (둘 다 유지).
- **경기력 스탯**: FotMob 리그 리더보드. 2026 은 풀세트, 2025 는 xG·xA·기회창출 3개만 보강.
- **Brand Fit**: 22명 중 공개 SNS가 있는 선수 위주로.

작성 규칙:
- `data/collect/*.csv` 의 **`Player` 열 이름은 절대 바꾸지 말 것** (스카우팅 인덱스와 정확히 일치해야 병합됨).
  발음기호 포함: `Marcão`, `Stefan Mugoša`, `Tiago Orobó`, `Jhon Montaño`, `Hólmbert Friðjónsson`.
- 못 찾은 값은 **빈칸**으로 두면 됨. 코드가 결측치를 처리함. **추정치를 넣지 말 것** (넣어야 하면 `notes`에 "추정" 명시).
- 숫자만 입력 (쉼표·단위·% 기호 제외). 예: `1500000` (O), `€1.5m` (X). `pass_acc_pct` 는 `82.4` 처럼 숫자만.

---

## 1. `data/collect/advanced_stats_2025.csv` — 최우선 (Tier 1)

**왜**: 지금 지표는 전부 "골/슈팅". 창출(키패스·xA), 전진(드리블·박스 터치), 결정력 품질(npxG 대비 실득점),
타깃형 자질(공중볼)이 통째로 비어 있음. 이걸 채우면 작은 표본(6경기짜리 마르캉 등) 신뢰도 문제도 크게 완화됨.

**소스** (택1, 일관되게):
- **FotMob** — `fotmob.com` → 선수 검색 → 선수 페이지 → "Season stats" → 2025 K League 1 선택.
  per-90 수치와 시즌 합계를 같이 보여줌. 가장 편함.
- **Sofascore** — `sofascore.com` → 선수 → "Statistics" → 2025 시즌. 항목명이 조금 다름 (아래 매핑).

| 컬럼 | 뜻 | FotMob 항목 | Sofascore 항목 | 없으면 |
|---|---|---|---|---|
| `npxg_90` | 페널티 제외 기대득점 /90 | Non-penalty xG per 90 | xG (Expected goals) 에서 페널티 xG 빼고 90분 환산 | 빈칸 |
| `xa_90` | 기대도움 /90 | Expected assists per 90 | Expected assists | 빈칸 |
| `key_passes_90` | 슈팅으로 이어진 패스 /90 | Chances created per 90 | Key passes per game | 빈칸 |
| `big_chances_created` | 결정적 기회 창출 (시즌 합계) | Big chances created | Big chances created | 빈칸 |
| `big_chances_missed` | 결정적 기회 놓침 (시즌 합계) | Big chances missed | Big chances missed | 빈칸 |
| `dribbles_won_90` | 성공한 드리블 /90 | Successful dribbles per 90 | Successful dribbles per game | 빈칸 |
| `touches_box_90` | 상대 박스 안 터치 /90 | Touches in opposition box per 90 | Touches in penalty area (per game) | 빈칸 |
| `aerials_won_pct` | 공중볼 경합 승률 % | Aerial duels won % | Aerial duels won (%) | 빈칸 |
| `fouls_drawn_90` | 얻어낸 파울 /90 | Fouls won per 90 | Was fouled (per game) | 빈칸 |
| `pass_acc_pct` | 패스 성공률 % | Pass accuracy % | Accurate passes (%) | 빈칸 |
| `minutes_total` | 2025 시즌 총 출전분 | Minutes played | Minutes played | 교차검증용, 가능하면 채움 |
| `source` | `fotmob` 또는 `sofascore` | | | 필수 |
| `collected_date` | 수집일 `YYYY-MM-DD` | | | 필수 |
| `notes` | 특이사항 (예: "2025 도중 이적", "리그컵 포함") | | | 선택 |

> FotMob/Sofascore 의 "K League 1 2025" 시즌이 우리 FBref 표본과 같은 시즌인지 반드시 확인.
> 두 소스의 출전분(`minutes_total`)이 FBref `90s × 90` 과 ±15% 이상 차이 나면 `notes`에 적어줘.

---

## 2. `data/collect/history.csv` — 성장세 (Tier 2)

**왜**: 원래 기획의 "Current Ability vs Potential 분리"를 여기서 실현. 최근 2~3시즌 생산성 추이로
"지금 잘하는 선수"와 "올라오는 선수"를 구분.

**대상**: 22명 중 **28세 이하 + 2025 생산성 상위** 선수 우선 (성장세가 의미 있는 대상).
  예: 이호재(25), Yago Cariello(27), Kim Sinjin(25), Jeong Jaemin(24), Abdallah Hleihil(25).
  나이 많은 선수는 굳이 안 해도 됨.

**소스**: FotMob 선수 페이지의 시즌별 표, 또는 Transfermarkt "Performance data" (`transfermarkt.com` → 선수 → Stats).

- 한 선수당 **여러 줄** (시즌마다 1줄). `season` 은 `2024`, `2023` 형식.
- `competition` 은 리그 이름 (`K League 1`, `K League 2`, `J1 League`, `Brazil Serie B` 등). 리그가 다르면 그대로 적어줘 — 리그 수준 차이는 나중에 감안.
- `npxg`, `xa` 는 과거 시즌이라 없을 수 있음 → 빈칸. `goals`, `assists`, `minutes`, `matches` 만이라도 OK.

---

## 3. `data/collect/bio.csv` — 에이전시 맥락 (Tier 2)

**왜**: 계약 기간·시장가치·나이·주발은 "장기계약 검토 / 리세일 밸류" 같은 에이전시 판단의 근거.

**소스**: **Transfermarkt** (`transfermarkt.com` → 선수 페이지 상단 박스).

| 컬럼 | 뜻 | 비고 |
|---|---|---|
| `dob` | 생년월일 `YYYY-MM-DD` | |
| `height_cm` | 키 (cm) | `188` |
| `weight_kg` | 몸무게 (kg) | 없으면 빈칸 |
| `preferred_foot` | `right` / `left` / `both` | |
| `nationality` | 주 국적 | |
| `nt_caps` | A대표팀 출전 수 | Transfermarkt "National team" 또는 위키 |
| `nt_goals` | A대표팀 득점 | |
| `market_value_eur` | 현재 시장가치 (유로, 숫자만) | `1200000` |
| `market_value_asof` | 그 시장가치 기준일 | Transfermarkt 표시일 |
| `contract_until` | 계약 만료 `YYYY-MM-DD` 또는 `YYYY` | |
| `boot_sponsor` | 축구화 브랜드 (Nike/adidas/Puma/Mizuno/New Balance…) | IG 사진·기사로 확인, 없으면 빈칸 |
| `transfermarkt_url` | 선수 페이지 URL | 출처 추적용 |
| `source` | `transfermarkt` 등 | |
| `collected_date` | 수집일 | |

---

## 4. `data/collect/brand_marketing.csv` — Brand Fit 고도화 (Tier 1, 파일럿 한정)

**왜**: 지금 참여율이 전부 추정치. 이걸 **실측**으로 바꾸는 게 이 프로젝트에서 전문성 인상을 가장 크게 바꿈.

### 4-1. 팔로워 & 성장

| 컬럼 | 방법 |
|---|---|
| `ig_handle` | 인스타 계정 (@ 제외). 공식 계정인지 확인 (동명이인·팬계정 주의) |
| `followers` | 현재 팔로워 수 (숫자만, `29900`) |
| `followers_asof` | 확인한 날짜 |
| `followers_prev` | 6~12개월 전 팔로워 수 — **Social Blade** (`socialblade.com/instagram/user/핸들`) 에서 과거 그래프 확인. 없으면 빈칸 |
| `followers_prev_date` | 그 수치의 시점 |

### 4-2. 참여율 (핵심)

최근 게시물 **10~12건**을 열어서 좋아요·댓글 수를 세어 평균낸다. (Reels/사진 섞여도 됨. 광고성 협찬 게시물, 경조사 게시물은 제외 권장.)

| 컬럼 | 방법 |
|---|---|
| `posts_sampled` | 실제로 센 게시물 수 (`10`) |
| `likes_avg` | 좋아요 평균 (숫자만) |
| `comments_avg` | 댓글 평균 |
| `sample_start` / `sample_end` | 샘플한 게시물의 가장 오래된/최근 날짜 |

→ 코드가 `참여율(%) = (likes_avg + comments_avg) / followers × 100` 로 계산. 추정치 컬럼은 폐기.

### 4-3. 멀티플랫폼 (선택)

`yt_subs`, `tiktok_followers`, `x_followers` — 있으면 채우고 없으면 빈칸.

### 4-4. 언론 노출 (1~5 손버킷 → 재현 가능한 수치로 교체)

| 컬럼 | 방법 |
|---|---|
| `news_count` | **네이버 뉴스**에서 선수 이름 검색 → 기간 필터를 최근 90일로 설정 → 검색 결과 건수 |
| `news_window_days` | `90` |
| `news_source` | `naver_news` |

### 4-5. 스폰서 & 이미지

| 컬럼 | 방법 |
|---|---|
| `boot_sponsor` | bio.csv 와 동일 |
| `other_sponsors` | IG 에서 `#광고` `#협찬`, 태그된 브랜드 계정, 브랜드와 찍은 사진 → 파이프로 구분 (`뱅크샐러드\|무신사`) |
| `image_tags` | 아래 어휘에서 골라 파이프로 구분 (이미 일부 채워둠) |
| `fanbase_breadth` | `domestic` / `regional` / `international` (해외 팬층 유무) |
| `story_note` | 마케팅 관점 한 줄 메모 (성장 서사, 특이 이력, 캐릭터) |

**image_tags 어휘** (이것만 사용):
`young_prospect`(젊은 유망주·성장서사), `national_team`(국가대표급), `veteran_leader`(베테랑·리더십),
`global_journey`(해외경험·글로벌), `family_man`(가정적), `flair_entertainer`(화려한 플레이·쇼맨십),
`hardworking_pro`(성실·프로페셔널), `underdog_story`(언더독·역경극복), `local_hero`(지역 연고 밀착).

---

## 우선순위 요약

| 순위 | 파일 | 효과 | 난이도 |
|---|---|---|---|
| 1 | `advanced_stats_2025.csv` (22명) | 스카우팅 모듈이 "골만 보는" 수준 → 제대로 된 스트라이커 프로파일 | 중 (선수당 3~5분) |
| 1 | `brand_marketing.csv` 4-2 참여율 (파일럿) | 참여율 추정 → 실측. 전문성 인상 급상승 | 중 (선수당 5~10분) |
| 2 | `history.csv` (유망주 5~8명) | Current Ability vs Potential 분리 실현 | 중 |
| 2 | `bio.csv` (22명) | 에이전시 판단 근거 (계약·시장가치·대표팀) | 하 (Transfermarkt 복붙) |
| 3 | `brand_marketing.csv` 나머지 (멀티플랫폼·성장률·언론) | 있으면 좋음 | 하~중 |

**최소 목표**: 파일 1번 22명 + 4-2 참여율 파일럿 → 이것만 해도 "파일럿"에서 "신뢰할 만한 분석"으로 격상.

데이터 채워서 주면 내가:
- percentile 을 스트라이커 22명 풀로 재계산
- 레이더를 득점/창출/전진/공중/결정력 5축 구조로 재설계
- npxG 대비 실득점으로 "결정력(finishing)" 축, xA·키패스로 "창출" 축 추가
- history 로 성장세 스파크라인 + Current/Potential 분리
- 참여율 실측 반영해 Marketability 재계산, 언론 노출을 news_count 기반으로 교체
- bio 로 Agency Recommendation 에 계약·시장가치·대표팀 근거 추가
