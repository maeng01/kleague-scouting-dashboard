"""언론 노출(media_exposure)을 재현 가능한 지표로 채우는 스크립트.

네이버 검색(뉴스) 응답의 `total`(해당 질의의 전체 뉴스 건수)을 읽어
`data/brand_fit_pilot.csv` 의 `news_count` 컬럼을 채운다.

왜 네이버인가:
- 국내 스포츠 선수의 언론 노출은 네이버 뉴스 색인이 사실상 표준.
- `total` 은 페이지네이션과 무관한 '전체 건수'라 재현 가능한 스칼라 지표로 쓰기 좋다.
- 자동 스크래핑(search.naver.com 크롤링)은 robots/ToS 문제 → 공식 API 만 사용.

⚠️ 2026 변경 — NAVER API HUB 로 이관
- 검색 API 가 developers.naver.com → **NAVER Cloud Platform 의 NAVER API HUB** 로 이관됨.
  신규 발급은 HUB 에서만 가능. (기존 developers.naver.com 키는 2027-06-30 까지 유예)
- 도메인: `openapi.naver.com` → `https://naverapihub.apigw.ntruss.com`
- 헤더: `X-Naver-Client-Id/Secret` → `X-NCP-APIGW-API-KEY-ID` / `X-NCP-APIGW-API-KEY`
- 뉴스 검색 경로: `/search/v1/news`
- 현재 무료 (검색 API 합산 월 775,000 회, 50 RPS)

준비:
1. https://console.ncloud.com/naver-api-hub/application 에서 Application 생성
   → 사용 API 에 '검색 - 뉴스' 체크 (원하면 '검색 - 블로그', '검색어트렌드'도)
2. 발급된 Client ID / Client Secret 을 환경변수로:
     export NCP_API_KEY_ID=xxxx
     export NCP_API_KEY=yyyy
   (구 developers.naver.com 키를 쓰는 유예 대상이면 NAVER_CLIENT_ID/SECRET 로 넣으면
    자동으로 구 엔드포인트로 폴백한다)
3. 질의어는 data/collect/naver_queries.csv 에서 읽는다 (player, query_ko).
   전수화하려면 이 CSV에 22명 행을 추가.

실행:
    python -m src.collect_naver               # news_count 갱신 + CSV 저장
    python -m src.collect_naver --dry-run     # 건수만 출력, 저장 안 함

주의:
- `total` 은 기간 필터가 없다(전체 색인 기준) → '최근 폼'이 아니라 '누적 인지도'에 가깝다.
  config.NEWS_COUNT_REF_LOW/HIGH 앵커도 그 스케일에 맞춰 둔다.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request

import pandas as pd

from . import config as C

HUB_URL = "https://naverapihub.apigw.ntruss.com/search/v1/news"
LEGACY_URL = "https://openapi.naver.com/v1/search/news.json"
QUERIES_CSV = C.DATA_DIR / "collect" / "naver_queries.csv"


def _client() -> tuple[str, dict[str, str]]:
    """(base_url, headers) — HUB 키가 있으면 HUB, 없으면 구 developers.naver.com 폴백."""
    hub_id = os.environ.get("NCP_API_KEY_ID")
    hub_key = os.environ.get("NCP_API_KEY")
    if hub_id and hub_key:
        return HUB_URL, {
            "X-NCP-APIGW-API-KEY-ID": hub_id,
            "X-NCP-APIGW-API-KEY": hub_key,
        }
    old_id = os.environ.get("NAVER_CLIENT_ID")
    old_key = os.environ.get("NAVER_CLIENT_SECRET")
    if old_id and old_key:
        return LEGACY_URL, {
            "X-Naver-Client-Id": old_id,
            "X-Naver-Client-Secret": old_key,
        }
    sys.exit(
        "인증 키가 없습니다.\n"
        "  NAVER API HUB:  export NCP_API_KEY_ID=... NCP_API_KEY=...\n"
        "  (구) 개발자센터: export NAVER_CLIENT_ID=... NAVER_CLIENT_SECRET=...\n"
        "발급: https://console.ncloud.com/naver-api-hub/application  (가이드: data/collect/COLLECT_NAVER.md)"
    )


def news_total(query: str, base: str, headers: dict[str, str]) -> int:
    url = f"{base}?query={urllib.parse.quote(query)}&display=1"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        return int(json.load(r)["total"])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    base, headers = _client()
    print(f"엔드포인트: {base}")

    if not QUERIES_CSV.exists():
        sys.exit(f"{QUERIES_CSV} 없음. player,query_ko 컬럼으로 만들어 주세요.")

    q = pd.read_csv(QUERIES_CSV)
    pilot = pd.read_csv(C.BRAND_FIT_CSV)

    counts: dict[str, int] = {}
    for _, r in q.iterrows():
        try:
            n = news_total(str(r["query_ko"]), base, headers)
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
