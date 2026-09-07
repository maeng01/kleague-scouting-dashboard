# docs/ — 기획·아카이브

프로젝트 루트를 깔끔하게 두기 위해 옮긴 문서·스크립트. **현재 동작 코드는 아님.**
살아있는 문서는 루트의 [`README.md`](../README.md)(구조·실행법), [`CLAUDE.md`](../CLAUDE.md)(작업 로그),
[`PORTFOLIO_1PAGER.md`](../PORTFOLIO_1PAGER.md)(지원서 첨부용).

| 파일 | 무엇 | 상태 |
|---|---|---|
| `football_talent_identification_scouting_model.md` | **처음 기획** — ML 기반 유소년 잠재력 예측 + 역사적 백테스팅 | 폐기(방향 재설정 배경). 왜 바꿨는지는 루트 README "왜 이 프로젝트인가" 참고 |
| `athlete_value_scouting_proposal.md` | 방향 재설정 후 작성한 전체 제안서 초안 | 참고용. 실제 구현은 코드/README 가 최신 |
| `DATA_COLLECTION.md` | 데이터 수집 범위·방침 메모 (2026-08) | 일부 섹션 폐기(선수별 페이지 방식 → FotMob 리더보드). 최신 수집 가이드는 [`data/collect/`](../data/collect/) |
| `kleague_scout_data.py` | soccerdata 로 FBref 자동 수집 시도한 스크립트 | 실패(FBref 봇 차단). 실제 데이터는 수동 CSV + `rebuild.py` |
