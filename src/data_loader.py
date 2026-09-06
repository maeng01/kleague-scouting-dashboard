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


def _archetype(row: pd.Series) -> str:
    """신장 + 드리블/키패스 점수 합 → 타깃형 / 기동·연결형 / 밸런스형.
    정밀 분류가 아니라 스카우팅 대화용 라벨 (공중볼 데이터가 없어 신장으로 대체)."""
    h, dr, kp = row.get("height_cm"), row.get("dribbles_90"), row.get("key_passes_90")
    if pd.isna(h) or pd.isna(dr):
        return "—"
    s = 0
    s += 2 if h >= 192 else 1 if h >= 188 else -1 if h <= 183 else 0
    s += 2 if dr <= 0.3 else 1 if dr <= 0.5 else -2 if dr >= 0.9 else -1 if dr >= 0.7 else 0
    if pd.notna(kp) and kp >= 1.3:
        s -= 1
    if s >= C.ARCHETYPE_TARGET_MIN:
        return "타깃형"
    if s <= C.ARCHETYPE_MOBILE_MAX:
        return "기동·연결형"
    return "밸런스형"


def load_strikers() -> pd.DataFrame:
    """2026 스트라이커 22명 (경기력 + percentile + 신뢰도 티어)."""
    df = pd.read_csv(C.STRIKERS_2026_CSV)
    df["age_display"] = df["age_years"].map(lambda a: f"{int(a)}세" if pd.notna(a) else "—")
    df["nation_code"] = df["Nation"].map(
        lambda n: str(n).split(" ")[-1] if pd.notna(n) else "—"
    )
    df["small_sample"] = df["90s"] < C.SMALL_SAMPLE_90S
    df["archetype"] = df.apply(_archetype, axis=1)
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


# 과정 6축의 2025 대응 컬럼 (없으면 2025 블렌드 스킵)
_BLEND_PAIRS = {
    "xg_90": "xg_90", "xa_90": "xa_90", "key_passes_90": "key_passes_90",
    "dribbles_90": "dribbles_90", "SoT_90": "sot_90",
    # Sh_90 은 2025 레이어에 없음 → 2026 값 그대로 (블렌드 안 함)
}


def blended_strikers(strikers: pd.DataFrame, prior: pd.DataFrame, decay: float = 0.6) -> pd.DataFrame:
    """과정 6축을 '표본 크기 가중 블렌드'로 재계산 + percentile 재산출.

    w_2026 = n26 / (n26 + decay·n25)  — 2026 출전이 많을수록 2026을 믿고,
    2025 표본이 클수록(완주 시즌) 그쪽으로 당겨진다. decay(<1)로 옛 시즌을 할인.
    2025 데이터가 없거나 미미하면 사실상 2026 값.
    """
    df = strikers.copy()
    if prior is None or prior.empty:
        return df
    p = prior.set_index("Player")
    n25_by = p["nineties_2025"].to_dict() if "nineties_2025" in p.columns else {}

    for m26, m25 in _BLEND_PAIRS.items():
        if m26 not in df.columns or m25 not in p.columns:
            continue
        new = []
        for _, r in df.iterrows():
            v26 = r.get(m26)
            n26 = float(r.get("90s", 0) or 0)
            name = r["Player"]
            v25 = p.at[name, m25] if name in p.index else None
            n25 = float(n25_by.get(name, 0) or 0)
            if v25 is None or pd.isna(v25) or n25 <= 0 or pd.isna(v26):
                new.append(v26)
                continue
            w26 = n26 / (n26 + decay * n25)
            new.append(round(w26 * float(v26) + (1 - w26) * float(v25), 3))
        df[m26] = new

    # percentile 재산출 (SNAPSHOT_METRICS 의 pct 컬럼)
    for m in C.SNAPSHOT_METRICS:
        key, pct = m["key"], m["pct"]
        if key in df.columns and df[key].notna().sum() >= 3:
            df[pct] = (df[key].rank(pct=True) * 100).round(1)
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
