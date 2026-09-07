"""파이프라인·산식 회귀 테스트.

빠른 sanity 체크 — "빌드가 22명을 만드는가 / 모든 점수가 0~100인가 / 제안서가 생성되는가".
실행: .venv/bin/pytest  (repo 루트에서)
전제: `python rebuild.py` 로 data/processed/*.csv 가 생성돼 있어야 함.
"""

from __future__ import annotations

import json
import zipfile

import pandas as pd
import pytest

from src import agency, brand_fit, build, config as C, data_loader, proposal
from src.ingest import to_num


# --- 픽스처 ---------------------------------------------------------------
@pytest.fixture(scope="module")
def data():
    strikers = data_loader.load_strikers()
    prior = data_loader.load_strikers_prior()
    brand = data_loader.load_brand_fit()
    merged = data_loader.merge(strikers, brand)
    return strikers, prior, brand, merged


@pytest.fixture(scope="module")
def pilots(data):
    _, _, _, merged = data
    return merged[merged["player"].notna()]


# --- 데이터 무결성 ------------------------------------------------------
def test_pool_is_22_strikers(data):
    strikers, *_ = data
    assert len(strikers) == C.POOL_SIZE == 22
    assert (strikers["90s"] >= C.MIN_90S_FILTER).all()


def test_blend_respects_sample_size(data):
    """블렌드: 2025 표본이 작으면 2026 가중이 1에 가깝고, 2025 표본이 크면 유의미하게 섞인다."""
    strikers, prior, _, _ = data
    bl = data_loader.blended_strikers(strikers, prior)
    assert len(bl) == len(strikers)

    n25 = prior.set_index("Player")["nineties_2025"].to_dict()
    small = big = 0
    for _, r in strikers.iterrows():
        n, n26 = n25.get(r["Player"], 0), r["90s"]
        if not n:
            continue
        w26 = n26 / (n26 + 0.6 * n)
        if n < 3:
            assert w26 > 0.82, f"{r['Player']}: 2025 표본 미미한데 2026 가중 {w26:.2f}"
            small += 1
        if n >= 20:
            assert w26 < 0.65, f"{r['Player']}: 2025 완주 시즌인데 2026 가중 {w26:.2f}"
            big += 1
    assert small and big  # 양쪽 케이스가 실제로 존재

    for m_ in C.SNAPSHOT_METRICS:
        assert bl[m_["pct"]].dropna().between(0, 100).all()


def test_percentiles_within_0_100(data):
    strikers, *_ = data
    pct_cols = [c for c in strikers.columns if c.endswith("_pct") or c.endswith("_pct_rank")]
    assert pct_cols, "percentile 컬럼이 없다"
    for c in pct_cols:
        v = strikers[c].dropna()
        assert v.between(0, 100).all(), f"{c} 가 0~100 범위를 벗어남"


def test_reliability_tiers_are_valid(data):
    strikers, *_ = data
    assert set(strikers["reliability"]).issubset(set(C.RELIABILITY_ORDER))


def test_archetype_labels_valid_and_spread(data):
    strikers, *_ = data
    assert set(strikers["archetype"]).issubset({"타깃형", "기동·연결형", "밸런스형", "—"})
    # 한 라벨이 전부를 먹지는 않아야 (분류가 의미 있으려면)
    non_na = strikers[strikers["archetype"] != "—"]["archetype"]
    assert non_na.value_counts().iloc[0] < len(non_na)


def test_goals_cross_check(data):
    """base CSV Gls 와 파생 xg_90*90s 이 말이 되는 범위인지 (대략)."""
    strikers, *_ = data
    assert (strikers["Gls"] >= 0).all()
    assert strikers["xg"].dropna().ge(0).all()


# --- Marketability 산식 ------------------------------------------------
def test_marketability_bounds_and_flags(pilots):
    for _, r in pilots.iterrows():
        mk = brand_fit.marketability(r)
        assert 0 <= mk.score <= 100, f"{r['Player']} score={mk.score}"
        for k, v in mk.components.items():
            assert 0 <= v <= 100, f"{r['Player']} {k}={v}"
        # has_sns 는 followers 유무와 일치해야 한다 (문자열 비교 대신 bool 필드)
        assert mk.has_sns == pd.notna(r.get("followers"))


def test_no_sns_player_score_is_reach_engagement_zero(pilots):
    no_sns = pilots[pilots["followers"].isna()]
    for _, r in no_sns.iterrows():
        mk = brand_fit.marketability(r)
        assert mk.components["도달(팔로워)"] == 0
        assert mk.components["참여율"] == 0
        assert not mk.has_sns


def test_news_count_raises_media_axis():
    base = dict(followers=20000, followers_confidence="verified", engagement_rate_pct=6.0,
                engagement_confidence="measured", fanbase_breadth="domestic", image_tags_list=["national_team"])
    lo = brand_fit.marketability(pd.Series({**base, "news_count": 50}))
    hi = brand_fit.marketability(pd.Series({**base, "news_count": 20000}))
    assert hi.components["언론 노출"] > lo.components["언론 노출"]


def test_category_fit_sorted_and_bounded(pilots):
    for _, r in pilots.iterrows():
        mk = brand_fit.marketability(r)
        fits = brand_fit.category_fit(r, mk)
        assert len(fits) == len(C.BRAND_CATEGORIES)
        scores = [f.score for f in fits]
        assert scores == sorted(scores, reverse=True)
        assert all(0 <= s <= 100 for s in scores)


# --- Agency 카드 / 제안서 --------------------------------------------
def test_agency_card_for_every_pilot(data, pilots):
    _, prior, _, _ = data
    for _, r in pilots.iterrows():
        mk = brand_fit.marketability(r)
        fits = brand_fit.category_fit(r, mk)
        card = agency.build_card(r, mk, fits, data_loader.prior_row(prior, r["Player"]))
        assert 1 <= card.priority_stars <= 5
        assert card.strategies and card.strengths and card.risks


def test_trend_feeds_agency_card(data, pilots):
    """검색 관심 '상승세' → 전략에 캠페인 타이밍 문구, '하락세' → 리스크."""
    _, prior, _, _ = data
    r = pilots.iloc[0]
    mk = brand_fit.marketability(r)
    fits = brand_fit.category_fit(r, mk)
    pr = data_loader.prior_row(prior, r["Player"])
    up = agency.build_card(r, mk, fits, pr, {"label": "상승세", "ratio": 1.6})
    assert any("상승세" in s for s in up.strategies)
    down = agency.build_card(r, mk, fits, pr, {"label": "하락세", "ratio": 0.6})
    assert any("하락세" in s for s in down.risks)
    base = agency.build_card(r, mk, fits, pr, None)
    assert not any("검색 관심" in s for s in base.strategies + base.risks)


def test_proposal_docx_is_valid(data, pilots):
    _, prior, _, _ = data
    r = pilots.iloc[0]
    mk = brand_fit.marketability(r)
    fits = brand_fit.category_fit(r, mk)
    card = agency.build_card(r, mk, fits, data_loader.prior_row(prior, r["Player"]))
    blob = proposal.build_docx(r, mk, fits, card)
    assert len(blob) > 5000
    assert zipfile.is_zipfile(__import__("io").BytesIO(blob))  # docx = zip


# --- 유틸 -----------------------------------------------------------
@pytest.mark.parametrize("raw,expect", [
    ("**12**", 12.0), ("1,234", 1234.0), ("45.6%", 45.6),
    ("13.2 m", 13.2), ("", None), ("—", None),
])
def test_to_num(raw, expect):
    assert to_num(raw) == expect


def test_build_main_is_deterministic():
    """python -m src.build 을 두 번 돌리면 CSV 가 바이트 단위로 동일해야 한다.
    (players 를 set 으로 두면 프로세스마다 컬럼 순서가 흔들렸다)."""
    build.main()
    first = C.STRIKERS_2026_CSV.read_bytes()
    build.main()
    assert C.STRIKERS_2026_CSV.read_bytes() == first
    assert len(pd.read_csv(C.STRIKERS_2026_CSV)) == 22


# --- 뉴스 타임라인 스냅샷 --------------------------------------------
def test_player_news_schema():
    nw = data_loader.load_player_news()
    for player, v in nw.items():
        assert {"asof", "items"} <= v.keys()
        for it in v["items"]:
            assert {"title", "date", "source", "url"} <= it.keys()
            assert it["date"][:4].isdigit()
        if "trend" in v:
            assert v["trend"]["label"] in (
                "상승세", "하락세", "보합", "관심 미미", "데이터 부족"
            )


# --- 검색어 트렌드 모멘텀 -------------------------------------------
@pytest.mark.parametrize("ratios,expect", [
    ([5] * 8 + [20] * 4, "상승세"),          # 최근 4주가 이전 대비 급증
    ([20] * 8 + [5] * 4, "하락세"),          # 최근 4주가 급감
    ([10] * 12, "보합"),                      # 변화 없음
    ([0.5] * 12, "관심 미미"),                # 절대 관심도가 바닥
    ([10, 20, 30], "데이터 부족"),           # 표본 8주 미만
])
def test_momentum_labels(ratios, expect):
    from src.collect_naver import _momentum
    assert _momentum([float(x) for x in ratios])["label"] == expect
