# 프로젝트: K리그 선수 스카우팅 & 브랜드 적합도 대시보드

## 배경 및 목적

스포츠 에이전시(브리온 등) 및 향후 스포츠 브랜드 엔도스먼트 직무 지원용 포트폴리오 프로젝트.
원래 기획(`football_talent_identification_scouting_model.md`)은 ML 기반 잠재력 예측·역사적
백테스팅에 초점이 맞춰져 있었으나, 아래 이유로 방향을 재설정함:

1. 유소년 historical dataset은 공개 확보가 사실상 불가능 (survivorship bias 있는 표본 구하기 어려움)
2. 지원 직무(선수 매니지먼트/스폰서십 유치, 향후 브랜드 엔도스먼트)는 ML 예측 정확도보다
   "이 선수를 어떻게 관리하고 어떤 브랜드와 연결할지"에 대한 의사결정 지원을 필요로 함
3. 실제 업계에서도 에이전시/브랜드가 직접 ML 모델을 만들기보다 Nielsen Sports, Hookit,
   Opendorse, Q Score 같은 상용 플랫폼을 구매해서 쓰는 경우가 대부분 → 이 프로젝트는
   "그 로직을 이해하고 구현해본 역량 증명"으로 포지셔닝. 상용 플랫폼 대체 목적이 아님.

## 최종 방향 (비중 순서)

1. **Scouting Snapshot** (경기력 기초 맥락, 비중 작게) — 구현 완료 (`src/snapshot.py`)
2. **Brand Fit & Marketability** (핵심, 비중 크게) — 구현 완료 (`src/brand_fit.py`).
   파일럿 10명(`data/brand_fit_pilot.csv`) 대상. Marketability(참여율 최대 가중) +
   이미지 태그 기반 카테고리 적합도(활성화 계수 방식).
3. **Agency Recommendation** — 구현 완료 (`src/agency.py`, `src/proposal.py`).
   규칙 기반 강점/리스크/전략/우선순위 + .docx 제안서 초안 생성.

전체 제안서는 `athlete_value_scouting_proposal.md`, 구조·실행법은 `README.md` 참고.
Streamlit 앱: `app.py` (4개 페이지). 실행 `./run.sh` 또는 `.venv/bin/streamlit run app.py`.

## 구현 상태 (2026-08-28)

MVP 1차 통합 완료 — 3개 모듈 + 케이스 스터디 + 방법론 페이지가 Streamlit 대시보드로 동작.
`.venv/` 에 streamlit·plotly·pandas·python-docx 설치됨.

### Brand Fit 파일럿 10명 (GplusA_90 상위 + 경기수 보정 기준)

Lee Dong-gyeong, Joo Min-kyu, Patryk Klimala, Stefan Mugoša, Yago Cariello,
Tiago Orobó, Matheus Oliveira Santos, Marcão, Abdallah Hleihil, Lee Hojae.
- 팔로워: Lee Dong-gyeong/Joo Min-kyu/Klimala/Mugoša/Yago 는 IG 프로필에서 직접 확인,
  Tiago/Matheus 는 검색 스니펫 기반 미검증(confidence=low),
  Marcão/Hleihil/Lee Hojae 는 공개 개인 SNS 미확인(followers 공란 → marketability "제한적").
- 참여율(engagement_rate_pct)은 전부 팔로워 티어 기반 러프 추정치. 실제 분석 시
  최근 게시물 10건 (좋아요+댓글)/팔로워 로 교체해야 함.
- 데이터 확장: `data/brand_fit_pilot.csv` 에 행 추가하면 자동 반영 (Player 명은
  스카우팅 인덱스 CSV의 Player 컬럼과 정확히 일치해야 함, 이름 표기·발음기호 포함).

## ⚠️ 시즌 라벨 오류 발견 (2026-08-28) — 최우선 확인

`kleague_2025_attackers_scouting_index.csv` 및 `kleague_*_raw.csv` 는 파일명·문서상 "2025"라고
돼 있지만 **실제로는 2026 시즌 진행 중(~8월, 약 25R 시점) 데이터**임. 근거:
- 사용자가 FotMob에서 직접 붙여넣은 **2026 시즌** xG 리스트의 득점 수와 base CSV 의 `Gls` 가
  13명 전원 **정확히 일치** (Lee Dong-gyeong 9G/7A, Joo Min-kyu 5G, Lee Hojae 8G, Yago 11G…).
- 완료된 2025 시즌은 Lee Hojae 15골(뉴스 확인), Joo Min-kyu 14골 수준 → base CSV 와 전혀 다름.
- base CSV 최대 `90s` = 23.2 → 완주 시즌(30+)이 아니라 진행 중.

**함의**:
- `data/collect/2026 Stats/*.md`(사용자 수집) = base CSV 와 **같은 시즌** → 바로 병합 가능.
- `data/collect/2025 Stats/*.md` = 진짜 완료된 2025 시즌 → "직전 시즌 / Current Ability 기준" 레이어.
- 프로젝트 전반의 "2025 시즌" 표기를 "2026 시즌 (YYYY-MM-DD 기준, N R)"로 정정해야 함
  (CLAUDE.md·proposal·app.py·README·config.py). 아직 안 함 — 사용자 확인 후.

## 데이터 상황 (중요 — 반드시 숙지)

- **대상**: K리그1, 공격 포지션(Pos에 FW 포함), 2025시즌
- **소스**: FBref (fbref.com/en/comps/55) — Standard Stats + Shooting Stats 두 표만 수동으로
  받아옴 (자동 스크래핑은 FBref 봇 차단으로 실패, 사람이 브라우저에서 CSV 내보내기함)
- **표본**: 전체 공격진 118명 중 90s(90분 환산 출전) ≥ 5 필터링한 **68명**만 사용
  → 이 68명 풀 내에서만 percentile 계산됨. "K리그 전체 대비"가 아님을 항상 명시할 것
- **한계**: 90s≥5도 여전히 작은 표본. 흘레이힐(6.4경기), 마르캉(6.3경기)처럼 적은 경기 수인데
  percentile이 극단적으로 높게 나온 케이스 있음 → 대시보드에 90s 값을 percentile 옆에 항상
  같이 표시해서 표본 크기를 투명하게 보여줘야 함
- **완성된 결과물**: `kleague_2025_attackers_scouting_index.csv` (68명, Per-90 지표 +
  percentile rank 포함: Gls_90, Ast_90, GplusA_90, Sh_90, SoT_90, SoT_pct, Conversion)
- **수집 스크립트**: `kleague_scout_data.py` (soccerdata 라이브러리용으로 작성했으나 FBref
  봇 차단으로 실패함 — 참고용으로만 남겨둠, 실제 데이터는 수동 CSV로 확보함)

### FBref 관련 중요 제약 (2026년 1월 발생, 매우 중요)

FBref는 2026년 1월 20일부로 데이터 제공사 Stats Perform(Opta)과의 계약이 종료되어
**Passing, Possession, GCA, Defense, Miscellaneous 등 고급 스탯이 전 리그에서 삭제됨**.
이제 FBref에서 무료로 얻을 수 있는 건 Standard + Shooting 정도가 한계임. 이 사실을 모르고
"Possession/GCA 표를 받아달라"고 안내했다가 사용자가 실제로 없는 걸 확인해서 정정한 바 있음.
앞으로 FBref 기반 작업 시 이 제약을 항상 전제로 할 것.

### K리그 공식 데이터포털(data.kleague.com) 관련 중요 제약

이 사이트는 **robots.txt로 자동화 접근을 명시적으로 금지**하고 있음. 따라서 이 사이트에 대한
스크래퍼는 만들지 않기로 함 (사용자 로컬 실행용으로도 제공하지 않음). 필요시 상위 후보 선수
소수에 대해 사람이 직접 화면을 보고 수동으로 몇 가지 지표만 확인하는 보완 용도로만 사용.

## 다음 라운드: 포지션 특화 + 데이터 확장 (2026-08-28 결정)

사용자가 추가 데이터를 수집해서 주기로 함. 확정 사항:
- **포지션 범위**: 스트라이커만 (`Pos == "FW"`, 22명). percentile 을 이 22명 풀로 재계산할 것.
  (얇으면 `FWMF` 15명 합쳐 37명 옵션 — 수집 후 판단)
- **고급 스탯**: 22명 전원 대상 (xG/npxG, xA, key passes, big chances, dribbles, touches in box,
  aerials, fouls drawn, pass acc). 소스: FotMob 또는 Sofascore 수동 (FBref Opta 삭제 때문).
- **시즌 방침 (2026-08-28 갱신)**: 2025 완료 시즌 = "Current Ability" 기준, 2026 현재 시즌(진행 중)
  = "현재 폼·성장세" 레이어. 둘 다 유지해서 원래 기획의 CA vs Potential 분리를 데이터로 구현.
- **경기력 스탯 수집 = FotMob 리그 리더보드** (지표 1개 = 페이지 1개, 전 선수). 가이드:
  `data/collect/COLLECT_FOTMOB.md`. 파서: `src/ingest_fotmob.py` (FotMob URL 안 선수 ID로 매칭).
  - 2026: goals/assists/xg/xa/chances_created/big_chances/shots_on_target/dribbles/fouls_won/minutes/appearances
  - 2025: xg/xa/chances_created 3개만 (FBref Standard+Shooting 보강용)
  - 붙여넣은 raw 는 `data/collect/fotmob_20XX/<metric>.md`, 맨 윗줄 `# metric=xg season=2026 asof=...`.
  - 이미 받음: `data/collect/fotmob_2026/xg.csv` (2026 xG, 풀 관련 23명 발췌).
- `data/collect/` 나머지: `bio.csv`(Transfermarkt 수동), `brand_marketing.csv`(SNS·뉴스 수동),
  `history.csv`(2023~24, 유망주만·선택). `Player` 열은 스카우팅 인덱스와 정확히 일치하도록 프리필.
## 옵션 B 파이프라인 (2026-08-28 구축 완료)

사용자가 FotMob 리더보드를 `2026 Stats/` `2025 Stats/` 에 markdown 표로 저장 → `python rebuild.py`
→ `data/processed/strikers_2026.csv` `strikers_2025.csv` 재생성 (percentile·신뢰도 티어 포함).
자동 스크래핑은 안 함 (FBref 봇차단 / kleague.com robots.txt / **FotMob ToS가 스크래핑 금지** —
셋 다 금지라 사용자가 수동 복사·업로드, 나는 파싱·재계산만).

- `src/ingest.py` — markdown 표 파서 + FotMob 리더보드 raw 파서 + `to_num()`
- `src/statfiles.py` — 파일별 {원본 컬럼 → 정규 지표} 매핑. **새 지표 파일 오면 여기 한 줄 추가**
- `data/name_map.csv` — FotMob 로마자명 → base CSV Player (FW 21명 매핑, Kong Minhyu 는 FotMob 데이터 없음)
- `src/build.py` / `rebuild.py` — 오케스트레이터. 교차검증(도움 base vs 파일)·0채움(리더보드 누락=~0)·리포트
- 출력 `data/processed/_build_report.md` 에 매칭/결측 현황

### 현재 수집 상태 (strikers, FW 22명 풀) — 2026-08-29
- **2026**: 거의 완성. base CSV + xG·xA·키패스·빅찬스±·유효슈팅정확도·드리블 = **21/22**
  (Kong Minhyu 만 FotMob 무존재). 피파울은 PK 획득자 7/22 (부분, 옵션).
- **2025 (직전 시즌 레이어)**: xG·xA·기회창출·**출전(경기수·분)**·드리블·유효슈팅 = **14/22명** 커버
  (나머지 8명은 2026 신규 영입이라 2025 K1 기록 없음/미미 — 정상). Yago·Klimala 등은
  2025 표본이 4~5경기라 신뢰도 낮음 티어로 자동 분류됨.

### 동명이인 처리 (중요)
2026 K리그1 에 `Gun-Hee Kim` 2명 존재. `src/build.py._collect_season` 이 골/도움 컬럼 있는 파일은
base Gls/Ast 대조로 올바른 줄 선택, 없는 파일은 스킵(NaN). `_row_goal_assist` 는 '편차 (득점-xG)'
같은 파생 컬럼을 제외해야 함 (안 하면 마지막 매칭이 편차값으로 덮어써서 오선택). 새 동명이인
생기면 `data/name_map.csv` + 이 로직 확인.

### app.py 리팩터 완료 (2026-08-29)
- app 이 `data/processed/strikers_2026.csv` + `strikers_2025.csv` 를 읽음 (`src/data_loader.load_strikers*`)
- 레이더·percentile = 과정지표 6축(xG/90·슈팅/90·유효슈팅/90·xA/90·키패스/90·드리블/90)만
- 결과지표(득점/90·결정력 finishing_90 = Gls_90−xg_90·전환율)는 별도 표 + "변동성 큼" 경고
- 신뢰도 티어 🟢안정(1800+)/🟡중간(900~1800)/🔴낮음(<900) — `src/build.py._reliability`
- ① 탭에 2025→2026 rate 비교(grouped bar), Agency 카드는 `build_card(..., prior)` 로 전년 대비 추세 반영
- `config.SNAPSHOT_METRICS` / `OUTCOME_METRICS` / `RADAR_METRICS` 가 새 컬럼 기준
- `brand_fit_pilot.csv` 는 스트라이커 풀 11명으로 교체 (이동경·Matheus 는 2선이라 제외)
- 방법론 페이지에 표본 안정화(과정 vs 결과 지표) 설명 추가

### bio.csv 완료 (2026-08-29)
- 22명 전원 Transfermarkt 에서 수집 (내가 Browser pane 으로 각 선수 페이지 직접 조회 — WebFetch 는
  TM 차단, Browser pane 은 됨). dob·height·foot·nationality·market_value·contract_until·boot_sponsor.
- nt_caps/nt_goals: 22/22 수집 (TM 프로필 "Caps/Goals" — 대부분 A대표 기준). Mugoša 65/16,
  Klimala 11/4, 주민규 11/3, Hólmbert 6/2 등. Agency 카드가 nt_caps≥10 → "A대표 정착" 강점.
- preferred_foot 21/22 (Jhon Montaño 만 공란 — TM 없음 + FotMob 슈팅 좌우 R5/L2로 애매).
  Hleihil·Tiago·Lee Kunhee 는 FotMob 슈팅 분포로 추정(right).
- weight_kg 17/22: 나무위키(한국선수 + 주요 외국인)에서 수집. Marcão는 나무위키 "말컹" 문서.
  미수집 5명(Hleihil·Diogo·Breno·Vitor Gabriel·Lee Kunhee)은 2026 신규 영입이라 나무위키 페이지
  없음 + TM/FotMob 체중 미표기. Choe Byeongchan 62kg·Kong Minhyu 70kg 는 나무위키 기준이나
  다소 가벼워 유의(notes 컬럼 참고). foot 은 22/22 (Hleihil·Tiago·Kunhee·Montaño 는 FotMob
  슈팅 좌우 분포/나무위키로 확정).
- **여전히 미수집**: contract_until 8/22 (나머지 TM "-" 비공개), boot_sponsor 2/22 (이호재 adidas,
  Hólmbert Nike — TM Outfitter 필드), market_value 21/22 (Kong Minhyu K4 이적).
- `src/build.py` 가 `data/collect/bio.csv` 병합 + `contract_years_left` 계산 (오늘 기준).
- Agency 카드: 계약 만료 임박(≤0.6년) 리스크, 저평가+기여양호 리스크, 신장≥191 타깃형 강점,
  boot_sponsor 강점. app 헤더·proposal.docx 에 선수정보 라인.
- 주의: TM "current club" 은 최신이라 base CSV(2026 진행중)와 다를 수 있음
  (Lee Hojae→Darmstadt, Jhon Montaño→Dibba SCC, Kong Minhyu→Siheung 등 시즌 중 이적). dob·height 등은 유효.

### 참여율 실측 완료 (2026-08-31)
파일럿 5명(handle 있는 스트라이커) IG 게시물별 좋아요/댓글을 **로그인 없이** `meta[og:description]`
("839 likes, 0 comments - ...")에서 읽어 최근 5~10건 평균. `data/collect/brand_marketing.csv` 에 원자료,
`data/brand_fit_pilot.csv` 의 engagement_rate_pct/confidence(measured|measured_likes_only) 갱신.
- Yago 20.7%(9.1K) · Mugoša 10.5%(21.7K) · Tiago 8.0%(20K) · Klimala 6.7%(45.4K) · 주민규 3.9%*(댓글 비활성)
- **팔로워↑ → 참여율↓** 실증. `config.ENGAGEMENT_REF_HIGH` 를 7→12 로 상향(K리그 팬덤 밀도 반영).
- `brand_fit.marketability` 가 confidence="높음(참여율 실측)" 표시.

### 아직 (선택 개선)
- 2025 유효슈팅·드리블 7/14 (부수), 2026 전체 피파울 리더보드 (현재 PK 7명)
- 최근가중 블렌드 뷰(2026×0.6 + 2025×0.4) 미구현 — 현재는 두 시즌 나란히만

### 언론 노출 실측 완료 (2026-09-06) — NAVER API HUB
- 2026년부터 네이버 검색 API 가 developers.naver.com → **NAVER API HUB(NCP)** 로 이관. 신규는 HUB 만.
  엔드포인트 `naverapihub.apigw.ntruss.com/search/v1/news`, 헤더 `X-NCP-APIGW-API-KEY-ID`/`-KEY`.
- 사용자가 HUB Client ID/Secret 발급 → `NCP_API_KEY_ID`/`NCP_API_KEY` env 로 `python -m src.collect_naver` 실행.
  (키는 커밋 안 함. brand_fit_pilot.csv 의 news_count 값만 커밋 → 배포엔 키 불필요)
- `src/collect_naver._client()` 가 HUB 키 우선, 없으면 구 `NAVER_CLIENT_ID/SECRET` 폴백.
- **파일럿 11명 news_count 수집**: 주민규 38211·무고사 18654·말컹(마르캉) 9350·이호재 8744·모따 5662·
  야고 4459·클리말라 2639·디오구 862·페리어 821·오로보 28·흘레이할 27.
  → `config.NEWS_COUNT_REF_LOW=40 / HIGH=50000` 로 앵커 조정. media 축이 이제 실측 기반.
- 질의어 주의: 마르캉→**말컹**(별명), Diogo→**디오고**(디오구 아님), Tiago→**티아고**,
  오로보·흘레이할은 표기 미정착으로 건수가 실제보다 낮음(naver_queries.csv 기록).

### 최근 뉴스 타임라인 (2026-09-06) — 선수 페이지
- 같은 API 로 관련도순 헤드라인 → **제목에 선수명 토큰이 든 기사만** 필터(팀 롤 소식 컷) →
  신디케이트 중복 제거 → 최신 6건. `data/collect/player_news.json` (수집 시점 스냅샷).
- `naver_queries.csv` 컬럼 개편: `count_query`(건수용) / `news_query`(타임라인용) / `news_filter`(제목 필수 토큰).
- app 선수 페이지: `player_news` 로드, ≥3건이면 "📰 최근 뉴스" expander, <3건이면 "언급 적음" 캡션.
- 표시됨: 주민규·클리말라·야고·이호재(다름슈타트)·모따·티아고·디오고. 미표시: 무고사·마르캉(결장)·흘레이할·페리어.
- **뉴스로 스탯 추출은 안 함** — API 가 본문 안 줌 + 뉴스 산문에 xG 없음. 스탯은 FotMob 유지.
- 갱신: `python -m src.collect_naver --news-only` (키 필요). 배포엔 json 만 있으면 됨.

### 검색 관심 추세 / 캠페인 타이밍 (2026-09-07) — NAVER 데이터랩
- 데이터랩 검색어트렌드 HUB 경로: `naverapihub.apigw.ntruss.com/search-trend/v1/search` (POST).
  `/datalab/*` 계열은 전부 404. body `{startDate,endDate,timeUnit:"week",keywordGroups:[{groupName,keywords}]}`,
  한 요청에 5그룹까지. 응답 `ratio` 는 **요청 배치 내 최고점=100 상대값** → 선수 간 비교 불가, 추세만.
- `src/collect_naver._momentum(ratios)` — 최근 약 18주 주간값 → **최근 4주 평균 ÷ 이전 8주 평균**
  → `상승세`(≥1.25)/`보합`/`하락세`(≤0.75)/`관심 미미`(양쪽 <2)/`데이터 부족`(8주 미만).
  `player_news.json` 의 `trend` 키로 저장.
- `naver_queries.csv` 에 `trend_query` 컬럼 추가(`;` 구분 = 키워드 그룹, 예 `말컹;마르캉`).
- 파일럿 11명: 상승세 클리말라·야고·오로보(티아고)·모따 / 하락세 페리어 / 보합 주민규·무고사·마르캉 /
  데이터 부족 흘레이할·이호재·디오고 (검색량 임계치 미만·표기 미정착).
- **Marketability 점수엔 안 넣음** — 상대 스케일이라. app 선수 페이지 + ②탭에 "캠페인/재계약 타이밍"
  참고 캡션으로만(`app._trend_caption`). 테스트: `test_momentum_labels`.

### 배포 + 콘텐츠 보강 (2026-09-06)
- **배포 완료**: GitHub `github.com/maeng01/kleague-scouting-dashboard` →
  Streamlit Community Cloud `https://kleague-striker-scouting.streamlit.app`.
  Python 3.12 로 고정(3.14 는 altair import 깨짐). `requirements.txt` 에 `altair==5.5.0` 핀.
- **포트폴리오 문서**: `README.md`(재구성) + `PORTFOLIO_1PAGER.md`(지원서 첨부용).
- **소개 & 사용법 페이지** 신설(첫 페이지, 기본 랜딩) — 3가지 질문/용어 6개/5분 워크스루/데이터 출처/한계.
- **케이스 스터디 대폭 보강**: `data/case_studies.json` 8건, `module` 필드로 3모듈 그룹핑.
  Osaka·손흥민·EMV·조규성·**누녜스(과정 vs 결과)**·**샤라포바 2016(브랜드 세이프티=이 도구 한계)**·
  김민재(재계약)·에이전시 업무 범위. app.py 케이스 스터디 페이지가 module별로 렌더 + source_note.
- **언론 노출 재현화 파이프라인**: `brand_fit_pilot.csv` 에 `news_count`/`news_count_asof` 컬럼,
  `src/brand_fit.py` 가 news_count 있으면 `log10` → media_score, 없으면 media_exposure 1–5 fallback.
  `config.NEWS_COUNT_REF_LOW/HIGH`(30/3000). `src/collect_naver.py`(네이버 검색 API `news.json` total,
  env NAVER_CLIENT_ID/SECRET), `data/collect/naver_queries.csv`, `data/collect/COLLECT_NAVER.md`.
  **값은 미수집** — 네이버 앱 등록(Client ID/Secret)은 사용자만 가능. Google News RSS 대안은 노이즈 커서 폐기.
- **참여율 확대 (Claude in Chrome 로그인 세션, 2026-09-06)**: 5명 → **7명**.
  - Marcão `markaooficial` (인증·103.4만·adidas football·참여율 3.2%) — mkt 16.8→54
  - Bruno Mota `bmota09` (비인증·8.7K·tapedesign 그립양말·참여율 ~15% 좋아요만) — mkt →63.1
  - 웹검색 핸들 부정확: `hj__lee19` 삭제됨, `brunomotacorreia`=심판. IG 자체 검색으로 재확인해야 함.
  - 2차(사용자가 링크 제공): Diogo `diogo7`(인증·7.8만·참여율 ~1.3% 낮음·가정적 이미지 강함) — mkt →42
    → 참여율 실측 **8명**.
  - 좋아요 비공개라 참여율 미측정(팔로워만): Abdallah Hleihil `abdallahlehel`(인증·1.8만·강원),
    Vitor Gabriel `v_gabriel09`(인증·16.9만).
  - **Lee Hojae: 개인 Instagram 없음(사용자 확인). 팬페이지만 존재** → SNS 축 0.
  - `measured_likes_only` note 문구 수정(댓글 비활성 → 좋아요만 집계).

## 아직 안 한 것 / 다음 단계

- [x] Brand Fit & Marketability 모듈 (파일럿 10명)
- [x] Radar Chart로 선수 프로필 시각화 (Streamlit)
- [x] Agency Recommendation 카드 + 제안서 초안(.docx) 생성
- [x] Streamlit 대시보드로 전체 통합
- [x] 참여율(engagement) 실측 (파일럿 5명) — 추가 확대는 IG 차단으로 보류
- [x] Streamlit Community Cloud 배포 + 포트폴리오 문서(README, 1pager)
- [x] 소개 & 사용법 페이지, 케이스 스터디 8건 보강
- [x] 언론 노출 재현화 — NAVER API HUB news_count 파일럿 11명 실측, media 축 반영
- [x] 최근가중 블렌드 뷰 (① 레이더 토글) / 플레이 아키타입 / 최근 뉴스 타임라인
- [x] 검색 관심 추세(데이터랩) — 캠페인 타이밍 신호, 파일럿 11명
- [x] pytest 25개 + GitHub Actions CI (rebuild + pytest)
- [ ] 파일럿 대상 확대 (IG 로그인 세션 필요) / 비파일럿 풀 news_count / README 스크린샷(마무리 시)
- [ ] (향후 확장, 이번 범위 제외) ML Potential Model, Historical Backtesting

## 톤 관련 주의사항

이 프로젝트를 발표/면접에서 소개할 때, "실제 업무 시스템을 대체한다"는 프레이밍은 쓰지 않음.
"업계 표준 분석 로직(참여율, brand fit 등)을 이해하고 직접 구현해본 학습/역량 증명 프로젝트"
라는 톤을 유지할 것. 표본이 작다는 한계도 숨기지 않고 명시하는 게 신뢰도에 더 도움이 됨.
