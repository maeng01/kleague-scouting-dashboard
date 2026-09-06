# 언론 노출(media_exposure) 재현 가능하게 만들기 — 네이버 뉴스 검색 건수

## 왜

지금 `brand_fit_pilot.csv` 의 `media_exposure` 는 1~5 **수동 버킷**이다. 자의적이고 재현이 안 된다.
이걸 **"고정 질의로 뉴스 검색했을 때 전체 건수"** 라는 재현 가능한 스칼라로 바꾼다.

- 소스: **네이버 검색 API** `GET /v1/search/news.json` → 응답의 `total` 필드
- `total` 은 페이지네이션과 무관한 '해당 질의의 전체 색인 건수' → 재현 가능
- 국내 스포츠 선수 언론 노출은 네이버 뉴스 색인이 사실상 표준

## 네이버 API가 꼭 필요한가?

**그렇다.** 대안을 다 검토했으나:

| 방법 | 문제 |
|---|---|
| `search.naver.com` 크롤링 | robots.txt / ToS 위반. 안 함 |
| Google News RSS 건수 | 최근 30일 창으로 좁혀도 100건에서 saturate + 외국인 선수 한글 표기 불일치로 노이즈 큼 → 점수 근거로 못 씀 |
| 네이버 검색 API `total` | **정답.** 무료. 단, 애플리케이션 등록(Client ID/Secret) 필요 |

애플리케이션 등록은 계정 소유자(사람)만 할 수 있다.

## 순서

### 1. 애플리케이션 등록 (약 2분, 무료)

1. https://developers.naver.com/apps/#/register 접속 (네이버 로그인)
2. 애플리케이션 이름: 아무거나 (예: `kleague-scouting`)
3. 사용 API: **검색** 체크
4. 환경: **WEB** 추가, URL 은 `http://localhost` 아무거나
5. 등록 완료 → **Client ID / Client Secret** 확인

무료 쿼터: 검색 API 일 25,000회 (22명 수집엔 차고 넘침).

### 2. 키 전달

```bash
export NAVER_CLIENT_ID=발급받은_ID
export NAVER_CLIENT_SECRET=발급받은_SECRET
```

### 3. 질의어 확정

`data/collect/naver_queries.csv` (player, query_ko, note) 를 열어 확인:
- 외국인 선수 한글 표기가 맞는지 (K리그 공식 표기 기준)
- 동명이인 있는 한국 선수는 **팀명 병기** (예: `이호재 포항`)
- 22명 전수화하려면 여기에 행 추가

### 4. 실행

```bash
python -m src.collect_naver --dry-run   # 건수만 확인
python -m src.collect_naver             # brand_fit_pilot.csv 의 news_count 갱신
```

앱은 자동 반영 (재빌드 불필요). `news_count` 가 채워지면 `src/brand_fit.py` 가
`media_exposure` 버킷 대신 `log10(news_count)` 를 0~100 으로 매핑해 Marketability 에 반영한다.

### 5. 앵커 조정

`src/config.py` 의 `NEWS_COUNT_REF_LOW` (기본 30) / `NEWS_COUNT_REF_HIGH` (기본 3000) 를
실제 수집된 분포를 보고 조정. (파일럿 11명 중앙값 근처가 50점이 되도록)

## 한계

- `news.json` 은 기간 필터가 없어 **전체 기간 누적 건수**다. "최근 폼"이 아니라
  "누적 인지도"에 가깝다. 최근 노출만 보려면 유료/별도 API 필요.
- 표기가 흔한 이름(이호재, 디오구)은 팀명을 넣어도 완벽히 분리되지 않을 수 있음 → `note` 컬럼에 기록.
