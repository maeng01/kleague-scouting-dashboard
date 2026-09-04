"""① Scouting Snapshot — 시각화 (Plotly).

레이더/막대는 전부 '과정' 지표의 percentile (2026 스트라이커 22명 풀 내부 기준).
결과 지표(득점률·결정력)는 표본에 느리게 안정되므로 여기 안 넣고 app 에서 별도 표기.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from . import config as C

_ACCENT = "#2E7D32"
_ACCENT_FILL = "rgba(46, 125, 50, 0.25)"
_GREY = "#9e9e9e"
_PRIOR = "#1E88E5"


def _pcts(row: pd.Series) -> tuple[list[str], list[float]]:
    labels, vals = [], []
    for m in C.SNAPSHOT_METRICS:
        labels.append(m["label"])
        v = row.get(m["pct"])
        vals.append(0.0 if pd.isna(v) else float(v))
    return labels, vals


def radar(row: pd.Series, compare: pd.Series | None = None) -> go.Figure:
    """선수 percentile 레이더 (2026, 과정 지표 6축). compare=다른 선수."""
    labels, values = _pcts(row)
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + values[:1], theta=labels + labels[:1], fill="toself",
        name=f"{row['Player']} · 2026", line=dict(color=_ACCENT), fillcolor=_ACCENT_FILL,
    ))
    if compare is not None:
        cl, cv = _pcts(compare)
        fig.add_trace(go.Scatterpolar(
            r=cv + cv[:1], theta=cl + cl[:1], fill="toself",
            name=str(compare["Player"]), line=dict(color=_GREY),
            fillcolor="rgba(158,158,158,0.15)",
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], tickvals=[25, 50, 75, 100])),
        showlegend=True, legend=dict(orientation="h", y=-0.15),
        margin=dict(l=60, r=60, t=20, b=40), height=420,
    )
    return fig


def percentile_bars(row: pd.Series) -> go.Figure:
    labels, pcts, raws = [], [], []
    for m in C.SNAPSHOT_METRICS:
        labels.append(m["label"])
        p = row.get(m["pct"])
        pcts.append(0.0 if pd.isna(p) else float(p))
        rv = row.get(m["key"])
        raws.append("—" if pd.isna(rv) else f"{float(rv):.2f}{m['unit']}")
    fig = go.Figure(go.Bar(
        x=pcts, y=labels, orientation="h",
        marker_color=[_band(p) for p in pcts],
        text=[f"{p:.0f}p · {r}" for p, r in zip(pcts, raws)],
        textposition="outside", cliponaxis=False,
    ))
    fig.update_layout(
        xaxis=dict(range=[0, 115], title="percentile (스트라이커 22명 풀 내부)",
                   tickvals=[0, 25, 50, 75, 100]),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=10, r=20, t=10, b=40), height=300,
    )
    return fig


def season_compare_bars(row_2026: pd.Series, row_2025: pd.Series | None) -> go.Figure | None:
    """2025 vs 2026 rate 비교 (per-90). 2025 데이터 없으면 None."""
    if row_2025 is None:
        return None
    metrics = [("xg_90", "xG/90"), ("xa_90", "xA/90"),
               ("Gls_90", "득점/90"), ("dribbles_90", "드리블/90")]
    rows = []
    for key, lab in metrics:
        v26 = row_2026.get(key)
        # 2025 프레임은 goals_90/xg_90/xa_90/dribbles_90 보유
        k25 = {"Gls_90": "goals_90"}.get(key, key)
        v25 = row_2025.get(k25)
        if pd.notna(v26):
            rows.append({"지표": lab, "시즌": "2026", "값": round(float(v26), 3)})
        if pd.notna(v25):
            rows.append({"지표": lab, "시즌": "2025", "값": round(float(v25), 3)})
    if not rows:
        return None
    d = pd.DataFrame(rows)
    fig = go.Figure()
    for season, color in [("2025", _PRIOR), ("2026", _ACCENT)]:
        sub = d[d["시즌"] == season]
        fig.add_trace(go.Bar(name=season, x=sub["지표"], y=sub["값"], marker_color=color))
    fig.update_layout(barmode="group", height=300, margin=dict(l=10, r=10, t=10, b=30),
                      legend=dict(orientation="h", y=-0.2))
    return fig


def _band(p: float) -> str:
    return "#2E7D32" if p >= 75 else "#66BB6A" if p >= 50 else "#FFB74D" if p >= 25 else "#E57373"
