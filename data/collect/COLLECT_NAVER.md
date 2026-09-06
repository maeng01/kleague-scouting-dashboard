# 언론 노출(media_exposure) 재현 가능하게 — 네이버 뉴스 검색 건수

## 왜

지금 `brand_fit_pilot.csv` 의 `media_exposure` 는 1~5 **수동 버킷**이다. 자의적이고 재현이 안 된다.
이걸 **"고정 질의로 뉴스 검색했을 때 전체 건수(`total`)"** 라는 재현 가능한 스칼라로 바꾼다.

- `total` 은 페이지네이션과 무관한 '해당 질의의 전체 색인 건수' → 재현 가능
- 국내 스포츠 선수 언론 노출은 네이버 뉴스 색인이 사실상 표준

## ⚠️ 2026: 네이버 검색 API 는 NAVER API HUB 로 이관됨

- 예전엔 `developers.naver.com` 에서 무료 발급 → **2026년부터 신규 발급은
  NAVER Cloud Platform 의 "NAVER API HUB" 에서만** 가능.
- `developers.naver.com` 은 이제 HUB 로 리다이렉트된다. 기존 키 보유자는 2027-06-30 까지 유예.
- 도메인·헤더·경로가 전부 바뀜:

| | 구 (developers.naver.com) | 신 (API HUB) |
|---|---|---|
| 도메인 | `openapi.naver.com` | `naverapihub.apigw.ntruss.com` |
| 뉴스 경로 | `/v1/search/news.json` | `/search/v1/news` |
| 인증 헤더 | `X-Naver-Client-Id` / `X-Naver-Client-Secret` | `X-NCP-APIGW-API-KEY-ID` / `X-NCP-APIGW-API-KEY` |
| 비용 | 무료 | 현재 무료 (검색 합산 월 77.5만 회, 50 RPS) |

`src/collect_naver.py` 는 두 방식을 **자동 감지**한다 — HUB 키(`NCP_API_KEY_ID/KEY`)가 있으면 HUB,
없고 구 키(`NAVER_CLIENT_ID/SECRET`)만 있으면 구 엔드포인트로 폴백.

## 등록 순서 (NAVER API HUB)

### 1. NCP 회원가입 / 로그인

https://www.ncloud.com → 로그인 (네이버 아이디 연동 가능). 결제수단 등록을 요구할 수 있으나
검색 API 는 현재 무료.

### 2. Application 생성

https://console.ncloud.com/naver-api-hub/application → **[Application 등록]**

- Application 이름: 아무거나 (예: `kleague-scouting`)
- **사용 API 선택** — 이 프로젝트에 유용한 것:
  - ✅ **검색 - 뉴스** (필수, `news_count` 에 쓰임)
  - ☐ 검색 - 블로그 (선택 — 팬·화제성 보조 지표로 확장 여지)
  - ☐ 검색어트렌드 (선택 — "검색량이 오르는 중인가" 모멘텀 신호. 별도 활용 코드 필요)
- 서비스 환경 / 인증: WEB, URL 은 `http://localhost` 등 아무거나

### 3. 인증 정보 확인

생성된 Application → **[인증정보]** 팝업에서 **Client ID / Client Secret** 복사.

### 4. 키 전달

```bash
export NCP_API_KEY_ID=발급받은_Client_ID
export NCP_API_KEY=발급받은_Client_Secret
```

### 5. 질의어 확정

`data/collect/naver_queries.csv` (player, query_ko, note) 확인:
- 외국인 선수 한글 표기가 맞는지 (K리그 공식 표기 기준)
- 동명이인 있는 한국 선수는 **팀명 병기** (예: `이호재 포항`)
- 22명 전수화하려면 여기에 행 추가

### 6. 실행

```bash
python -m src.collect_naver --dry-run   # 건수만 확인
python -m src.collect_naver             # brand_fit_pilot.csv 의 news_count 갱신
```

앱은 자동 반영 (재빌드 불필요). `news_count` 가 채워지면 `src/brand_fit.py` 가
`media_exposure` 버킷 대신 `log10(news_count)` 를 0~100 으로 매핑해 Marketability 에 반영한다.

### 7. 앵커 조정

`src/config.py` 의 `NEWS_COUNT_REF_LOW` (기본 30) / `NEWS_COUNT_REF_HIGH` (기본 3000) 를
실제 수집된 분포를 보고 조정. (파일럿 중앙값 근처가 50점이 되도록)

## 한계

- `total` 은 기간 필터가 없어 **전체 기간 누적 건수**다. "최근 폼"이 아니라 "누적 인지도"에 가깝다.
  최근 노출 추세가 필요하면 **검색어트렌드(DataLab)** API 를 별도로 붙여야 한다.
- 표기가 흔한 이름(이호재, 디오구)은 팀명을 넣어도 완벽히 분리되지 않을 수 있음 → `note` 컬럼에 기록.
