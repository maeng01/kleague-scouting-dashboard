"""처리된 데이터셋 로드 · 병합.

경기력 데이터는 `python rebuild.py` 로 생성된 data/processed/*.csv 를 읽는다.
(원본 수집 파일은 2026 Stats/ · 2025 Stats/, 파서는 src/build.py)
"""

from __future__ import annotations

import json

import pandas as pd

from . import config as C


def _years_left(contract_until) -> float | None:
    """계약 만료일까지 남은 연수 (오늘 기준). 연도만 있으면 연말로 간주."""
    if pd.isna(contract_until) or str(contract_until).strip() in ("", "-"):
        return None
    s = str(contract_until).strip()
    dt = pd.to_datetime(s, errors="coerce")
    if pd.isna(dt) and s[:4].isdigit():
        dt = pd.Timestamp(int(s[:4]), 12, 31)
    if pd.isna(dt):
        return None
    return round((dt - pd.Timestamp.today().normalize()).days / 365, 2)


def load_strikers() -> pd.DataFrame:
    """2026 스트라이커 22명 (경기력 + percentile + 신뢰도 티어)."""
    df = pd.read_csv(C.STRIKERS_2026_CSV)
    df["age_display"] = df["age_years"].map(lambda a: f"{int(a)}세" if pd.notna(a) else "—")
    df["nation_code"] = df["Nation"].map(
        lambda n: str(n).split(" ")[-1] if pd.notna(n) else "—"
    )
    df["small_sample"] = df["90s"] < C.SMALL_SAMPLE_90S
    # 결정력 = 실득점률 − 기대득점률
    if {"Gls_90", "xg_90"}.issubset(df.columns):
        df["finishing_90"] = (df["Gls_90"] - df["xg_90"]).round(3)
    # 계약 잔여연수는 '오늘' 기준이라 런타임 계산 (빌드 CSV 에 넣으면 날짜마다 drift)
    if "contract_until" in df.columns:
        df["contract_years_left"] = df["contract_until"].map(_years_left)
    return df


def load_strikers_prior() -> pd.DataFrame:
    """2025 완료 시즌 레이어 (직전 시즌 맥락). Player 기준, 있는 선수만."""
    try:
        return pd.read_csv(C.STRIKERS_2025_CSV)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Player"])


def load_brand_fit() -> pd.DataFrame:
    df = pd.read_csv(C.BRAND_FIT_CSV)
    df["image_tags_list"] = df["image_tags"].map(
        lambda s: [t for t in str(s).split("|") if t and t != "nan"]
    )
    df["has_sns"] = df["followers"].notna()
    return df


def load_case_studies() -> list[dict]:
    with open(C.CASE_STUDIES_JSON, encoding="utf-8") as f:
        return json.load(f)


def load_player_news() -> dict[str, dict]:
    """선수별 최근 뉴스 타임라인 스냅샷 (src/collect_naver.py 로 생성). 없으면 빈 dict."""
    path = C.DATA_DIR / "collect" / "player_news.json"
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def merge(strikers: pd.DataFrame, brand: pd.DataFrame) -> pd.DataFrame:
    return strikers.merge(brand, left_on="Player", right_on="player", how="left")


def prior_row(prior: pd.DataFrame, player: str) -> pd.Series | None:
    hit = prior.loc[prior["Player"] == player]
    return None if hit.empty else hit.iloc[0]
