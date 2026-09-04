# K리그 스트라이커 스카우팅 & 브랜드 적합도 대시보드 (파일럿)

스포츠 에이전시 / 브랜드 엔도스먼트 직무 지원용 포트폴리오. "이 선수를 어떻게 관리하고
어떤 브랜드와 연결할 것인가"라는 **의사결정 보조** 도구. 상용 플랫폼(Nielsen Sports, Hookit,
Wyscout 등) 대체가 아니라 그 분석 로직을 직접 구현해 이해도를 보이는 학습·역량 증명용.

## 실행

```bash
./run.sh
# 또는
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py
```

## 데이터 갱신 (수동 수집 → 자동 재빌드)

1. FotMob 리그 리더보드를 markdown 표로 `2026 Stats/` · `2025 Stats/` 에 저장
   (새 지표면 `src/statfiles.py` 에 컬럼 매핑 한 줄 추가)
2. `python rebuild.py` → `data/processed/*.csv` 재생성 (percentile·신뢰도 티어 포함)
3. `./run.sh`

자동 스크래핑은 하지 않음 — FBref 봇차단 / K리그 포털 robots.txt / FotMob ToS 모두 금지.
상세: `data/collect/COLLECT_FOTMOB.md`, 사고 배경: `DATA_COLLECTION.md`.

## 구성

| 페이지 | 내용 |
|---|---|
| 선수 대시보드 | 스트라이커 22명 필터 → 선수 상세 (3개 모듈 탭) |
| 파일럿 랭킹 | Brand Fit 파일럿 종합 순위 |
| 케이스 스터디 | Nike×오사카 등 엔도스먼트 사례 |
| 방법론 & 한계 | 데이터·산식·표본 안정화·한계 |

### 3개 모듈

1. **Scouting Snapshot** — 레이더/percentile 은 **표본에 빨리 안정되는 '과정' 지표** 6축
   (xG/90 · 슈팅/90 · 유효슈팅/90 · xA/90 · 키패스/90 · 드리블성공/90). 득점률·결정력(득점−xG)은
   '결과' 지표라 별도 표 + 변동성 경고. 90s·신뢰도 티어 항상 병기. 2025→2026 추세 비교.
2. **Brand Fit & Marketability** — Marketability(참여율 최대 가중) + 이미지 태그 기반 카테고리 적합도.
3. **Agency Recommendation** — 과정지표 percentile + 신뢰도 티어 + 연령 + 전년 대비 추세 + marketability
   → 규칙 기반 강점/리스크/전략/우선순위(★) + 1페이지 스폰서 제안서 초안(.docx).

## 데이터

- **base**: FBref Standard+Shooting. 파일명 `kleague_2025_...` 이지만 골·도움이 FotMob **2026**
  시즌과 일치 → 실제로는 **2026 진행 중** 스냅샷(약 25R). 풀 = `Pos=FW` & 90s≥5 → **22명**.
- **고급 지표**: FotMob 리그 리더보드 수동 수집 (`2026 Stats/`, `2025 Stats/`), `src/build.py` 로 파싱·병합.
- **직전 시즌 레이어**: 2025 완료 시즌 — 14/22명 커버 (나머지는 2026 신규 영입). 추세 비교용.
- **처리 결과**: `data/processed/strikers_2026.csv`, `strikers_2025.csv`, `_build_report.md`.
- **Brand Fit**: `data/brand_fit_pilot.csv` (수동, 스트라이커 11명), `data/case_studies.json`.

## 코드

```
app.py               Streamlit 엔트리 (4개 페이지)
rebuild.py           수집 파일 → data/processed/ 재생성
src/config.py        지표·가중치·임계값 ('초기 가설')
src/statfiles.py     수집 파일별 컬럼 → 정규 지표 매핑
src/ingest.py        markdown 표 / FotMob 리더보드 파서
src/build.py         오케스트레이터 (동명이인·교차검증·percentile·신뢰도 티어)
src/data_loader.py   processed CSV 로드·병합
src/snapshot.py      레이더 / percentile 막대 / 시즌 비교 (Plotly)
src/brand_fit.py     Marketability + 카테고리 적합도
src/agency.py        강점/리스크/전략/우선순위 규칙
src/proposal.py      제안서 초안 .docx 생성
data/name_map.csv    FotMob 로마자명 → base CSV Player
```

## 한계 (숨기지 않고 명시)

- 표본이 작고 시즌 진행 중 → "파일럿", 라운드 스냅샷임을 명시.
- 22명 중 15+90s 는 4명뿐 → 풀 절반이 저신뢰 구간. 그래서 과정/결과 지표를 분리하고 신뢰도 티어를 표시.
- SNS/참여율은 공개 API 제약으로 수작업·추정.
- Brand Fit 점수는 정성 판단 섞인 반정량 지표 — 예측이 아니라 의사결정 보조.
- ML Potential Model / Historical Backtesting 은 향후 확장 로드맵으로만 남김.
