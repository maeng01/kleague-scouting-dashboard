"""언론 노출(media_exposure)을 재현 가능한 지표로 채우는 스크립트.

네이버 검색 API `news.json` 의 응답 필드 `total`(해당 질의의 전체 뉴스 건수)을 읽어
`data/brand_fit_pilot.csv` 의 `news_count` 컬럼을 채운다.

왜 네이버인가:
- 국내 스포츠 선수의 언론 노출은 네이버 뉴스 색인이 사실상 표준.
- `total` 은 페이지네이션과 무관한 '전체 건수'라 재현 가능한 스칼라 지표로 쓰기 좋다.
- 자동 스크래핑(search.naver.com 크롤링)은 robots/ToS 문제 → 공식 API 만 사용.

준비:
1. https://developers.naver.com/apps/#/register 에서 애플리케이션 등록
   (사용 API: '검색' 체크). 무료. Client ID / Client Secret 발급.
2. 환경변수로 전달:
     export NAVER_CLIENT_ID=xxxx
     export NAVER_CLIENT_SECRET=yyyy
3. 질의어는 data/collect/naver_queries.csv 에서 읽는다 (player, query_ko).
   전수화하려면 이 CSV에 22명 행을 추가.

실행:
    python -m src.collect_naver               # news_count 갱신 + CSV 저장
    python -m src.collect_naver --dry-run     # 건수만 출력, 저장 안 함

주의:
- 네이버 `news.json` 의 `total` 은 '기간 필터'를 지원하지 않는다(전체 색인 기준).
  최근 N일로 좁히려면 별도 파라미터가 없으므로, 이 스크립트는 '전체 기간 total' 을 쓰고
  config.NEWS_COUNT_REF_LOW/HIGH 앵커도 그 스케일에 맞춰 둔다.
  (기간 한정이 꼭 필요하면 Datalab API 나 유료 옵션 검토.)
"""

from __future__ import annotations

import argparse
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

from . import config as C

API = "https://openapi.naver.com/v1/search/news.json"
QUERIES_CSV = C.DATA_DIR / "collect" / "naver_queries.csv"


def news_total(query: str, cid: str, secret: str) -> int:
    url = f"{API}?query={urllib.parse.quote(query)}&display=1"
    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", cid)
    req.add_header("X-Naver-Client-Secret", secret)
    with urllib.request.urlopen(req, timeout=10) as r:
        import json

        return int(json.load(r)["total"])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cid = os.environ.get("NAVER_CLIENT_ID")
    secret = os.environ.get("NAVER_CLIENT_SECRET")
    if not (cid and secret):
        sys.exit("NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 환경변수가 필요합니다. 파일 상단 주석 참고.")

    if not QUERIES_CSV.exists():
        sys.exit(f"{QUERIES_CSV} 없음. player,query_ko 컬럼으로 만들어 주세요.")

    q = pd.read_csv(QUERIES_CSV)
    pilot = pd.read_csv(C.BRAND_FIT_CSV)

    counts: dict[str, int] = {}
    for _, r in q.iterrows():
        try:
            n = news_total(str(r["query_ko"]), cid, secret)
        except Exception as e:  # noqa: BLE001
            print(f"  ! {r['player']}: {e}")
            continue
        counts[r["player"]] = n
        print(f"  {r['player']:<22} '{r['query_ko']}' → {n:,}건")
        time.sleep(0.2)  # rate limit 여유

    if args.dry_run:
        print("\n--dry-run: CSV 저장 안 함")
        return

    pilot["news_count"] = pilot.apply(
        lambda row: counts.get(row["player"], row.get("news_count")), axis=1
    )
    pilot["news_count_asof"] = pd.Timestamp.today().strftime("%Y-%m-%d")
    pilot.to_csv(C.BRAND_FIT_CSV, index=False)
    print(f"\n저장: {C.BRAND_FIT_CSV} ({len(counts)}명 news_count 갱신)")
    print("→ 앱은 자동 반영(재빌드 불필요). config.NEWS_COUNT_REF_* 앵커 확인 권장.")


if __name__ == "__main__":
    main()
