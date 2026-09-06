"""네이버 뉴스 검색으로 (1) 언론 노출 건수, (2) 선수별 최근 뉴스 타임라인을 수집.

- `news_count` : 고정 질의의 전체 뉴스 건수(`total`) → `data/brand_fit_pilot.csv` 의 컬럼.
  재현 가능한 media_exposure 지표. `src/brand_fit.py` 가 log10 스케일로 Marketability 에 반영.
- 뉴스 타임라인 : 최근 헤드라인 8건(제목·날짜·매체·링크) → `data/collect/player_news.json`.
  스탯이 아니라 '맥락'(부상·이적설·대표팀·연속골 등). app 선수 페이지에 스냅샷으로 표시.

왜 네이버인가:
- 국내 스포츠 선수의 언론 노출은 네이버 뉴스 색인이 사실상 표준.
- `total` 은 페이지네이션과 무관한 '전체 건수'라 재현 가능한 스칼라 지표로 쓰기 좋다.
- 자동 스크래핑(search.naver.com 크롤링)은 robots/ToS 문제 → 공식 API 만 사용.
- API 응답은 제목 + 200자 스니펫까지만 준다(본문 없음). 그래서 '스탯 추출'이 아니라 '타임라인'.

⚠️ 2026 변경 — NAVER API HUB 로 이관
- 검색 API 가 developers.naver.com → **NAVER Cloud Platform 의 NAVER API HUB** 로 이관됨.
  신규 발급은 HUB 에서만 가능. (기존 developers.naver.com 키는 2027-06-30 까지 유예)
- 도메인: `openapi.naver.com` → `https://naverapihub.apigw.ntruss.com`
- 헤더: `X-Naver-Client-Id/Secret` → `X-NCP-APIGW-API-KEY-ID` / `X-NCP-APIGW-API-KEY`
- 뉴스 검색 경로: `/search/v1/news`
- 현재 무료 (검색 API 합산 월 775,000 회, 50 RPS)

준비:
1. https://console.ncloud.com/naver-api-hub/application 에서 Application 생성
   → 사용 API 에 '검색 - 뉴스' 체크
2. 발급된 Client ID / Client Secret 을 환경변수로:
     export NCP_API_KEY_ID=xxxx
     export NCP_API_KEY=yyyy
   (구 developers.naver.com 키를 쓰는 유예 대상이면 NAVER_CLIENT_ID/SECRET 로 넣으면
    자동으로 구 엔드포인트로 폴백한다)
3. 질의어는 data/collect/naver_queries.csv 에서 읽는다
   (player, count_query=건수용, news_query=타임라인용, news_filter=제목 필수 토큰).

실행:
    python -m src.collect_naver               # news_count + 뉴스 타임라인 갱신
    python -m src.collect_naver --dry-run     # 출력만, 저장 안 함
    python -m src.collect_naver --news-only   # 타임라인만 갱신(건수는 그대로)

주의:
- `total` 은 기간 필터가 없다(전체 색인 기준) → '최근 폼'이 아니라 '누적 인지도'에 가깝다.
- 타임라인은 수집 시점 스냅샷이다. app 에 'YYYY-MM-DD 기준'으로 명시하고, 갱신하려면 재실행.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime

import pandas as pd

from . import config as C

HUB_BASE = "https://naverapihub.apigw.ntruss.com/search/v1/news"
LEGACY_BASE = "https://openapi.naver.com/v1/search/news.json"
QUERIES_CSV = C.DATA_DIR / "collect" / "naver_queries.csv"
NEWS_JSON = C.DATA_DIR / "collect" / "player_news.json"

_TAG = re.compile(r"<[^>]+>")


def _client() -> tuple[str, dict[str, str]]:
    """(base_url, headers) — HUB 키가 있으면 HUB, 없으면 구 developers.naver.com 폴백."""
    hub_id = os.environ.get("NCP_API_KEY_ID")
    hub_key = os.environ.get("NCP_API_KEY")
    if hub_id and hub_key:
        return HUB_BASE, {
            "X-NCP-APIGW-API-KEY-ID": hub_id,
            "X-NCP-APIGW-API-KEY": hub_key,
        }
    old_id = os.environ.get("NAVER_CLIENT_ID")
    old_key = os.environ.get("NAVER_CLIENT_SECRET")
    if old_id and old_key:
        return LEGACY_BASE, {
            "X-Naver-Client-Id": old_id,
            "X-Naver-Client-Secret": old_key,
        }
    sys.exit(
        "인증 키가 없습니다.\n"
        "  NAVER API HUB:  export NCP_API_KEY_ID=... NCP_API_KEY=...\n"
        "  (구) 개발자센터: export NAVER_CLIENT_ID=... NAVER_CLIENT_SECRET=...\n"
        "발급: https://console.ncloud.com/naver-api-hub/application  (가이드: data/collect/COLLECT_NAVER.md)"
    )


def _get(base: str, headers: dict[str, str], **params) -> dict:
    url = f"{base}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.load(r)


def _clean(s: str) -> str:
    return html.unescape(_TAG.sub("", s)).strip()


def _pub_iso(s: str) -> str:
    """RFC822 pubDate ('Sat, 23 Aug 2026 07:00:00 +0900') → 'YYYY-MM-DD' (기사 현지 날짜)."""
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return s[:16]


def _source(url: str) -> str:
    host = urllib.parse.urlparse(url).netloc.replace("www.", "")
    return host.split(".")[0] if host else ""


def news_total(query: str, base: str, headers: dict[str, str]) -> int:
    return int(_get(base, headers, query=query, display=1)["total"])


def _words(t: str) -> set[str]:
    return set(re.findall(r"[가-힣]{2,}", t))


def news_recent(
    query: str, base: str, headers: dict[str, str],
    filters: list[str] | None = None, keep: int = 6,
) -> list[dict]:
    """관련도순 최대 30건 → **제목**에 필터 토큰이 모두 든 기사만(팀 롤 소식 컷) →
    신디케이트 중복(제목 단어 자카드 > 0.45) 제거 → 최신순 keep 건."""
    items = _get(base, headers, query=query, display=30, sort="sim").get("items", [])
    out: list[dict] = []
    for it in items:
        title = _clean(it.get("title", ""))
        if filters and not all(f in title for f in filters):
            continue
        w = _words(title)
        if any(len(w & _words(o["title"])) / max(1, len(w | _words(o["title"]))) > 0.45 for o in out):
            continue
        link = it.get("originallink") or it.get("link", "")
        out.append({
            "title": title,
            "date": _pub_iso(it.get("pubDate", "")),
            "source": _source(link),
            "url": link,
        })
        if len(out) >= keep:
            break
    out.sort(key=lambda d: d["date"], reverse=True)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--news-only", action="store_true", help="타임라인만 갱신")
    args = ap.parse_args()

    base, headers = _client()
    print(f"엔드포인트: {base}")

    if not QUERIES_CSV.exists():
        sys.exit(f"{QUERIES_CSV} 없음. player,count_query,news_query,news_filter 컬럼으로 만들어 주세요.")

    q = pd.read_csv(QUERIES_CSV)
    today = pd.Timestamp.today().strftime("%Y-%m-%d")

    counts: dict[str, int] = {}
    timeline: dict[str, dict] = {}
    for _, r in q.iterrows():
        player = str(r["player"])
        count_q = str(r.get("count_query") or r.get("query_ko") or "")
        news_q = str(r.get("news_query") or count_q)
        filters = [t for t in str(r.get("news_filter") or "").split("|") if t]
        try:
            if not args.news_only:
                counts[player] = news_total(count_q, base, headers)
            recent = news_recent(news_q, base, headers, filters)
        except Exception as e:  # noqa: BLE001
            print(f"  ! {player}: {e}")
            continue
        timeline[player] = {"query": news_q, "asof": today, "items": recent}
        c = f"{counts[player]:,}건 · " if player in counts else ""
        print(f"  {player:<20} {c}타임라인 {len(recent)}건" + (f"  (최신 {recent[0]['date']})" if recent else "  ✗"))
        time.sleep(0.2)  # rate limit 여유

    if args.dry_run:
        print("\n--dry-run: 저장 안 함")
        if timeline:
            first = next(iter(timeline.values()))
            for it in first["items"][:3]:
                print(f"    · {it['date']} [{it['source']}] {it['title']}")
        return

    NEWS_JSON.write_text(
        json.dumps(timeline, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"\n저장: {NEWS_JSON} ({len(timeline)}명 타임라인)")

    if counts:
        pilot = pd.read_csv(C.BRAND_FIT_CSV)
        pilot["news_count"] = pilot.apply(
            lambda row: counts.get(row["player"], row.get("news_count")), axis=1
        )
        pilot["news_count_asof"] = today
        # NaN 있는 정수 컬럼이 float(29600.0)로 새는 걸 방지 — nullable Int64
        for c in ("followers", "media_exposure", "news_count"):
            if c in pilot.columns:
                pilot[c] = pd.to_numeric(pilot[c], errors="coerce").astype("Int64")
        pilot.to_csv(C.BRAND_FIT_CSV, index=False)
        print(f"저장: {C.BRAND_FIT_CSV} ({len(counts)}명 news_count 갱신)")

    print("→ 앱은 자동 반영(재빌드 불필요). config.NEWS_COUNT_REF_* 앵커 확인 권장.")


if __name__ == "__main__":
    main()
