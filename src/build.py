"""수집 파일 → 처리된 스트라이커 데이터셋 재생성.

사용:  python -m src.build
입력:  data/kleague_2025_attackers_scouting_index.csv  (실제로는 2026 시즌, 아래 SEASON_BASE)
       2026 Stats/*.md, 2025 Stats/*.md  (src/statfiles.py 에 등록된 것)
       data/name_map.csv
출력:  data/processed/strikers_2026.csv  (경기력 + percentile + 신뢰도 티어)
       data/processed/strikers_2025.csv  (직전 시즌 레이어, 있는 지표만)
       data/processed/_build_report.md   (매칭/결측 리포트)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from . import config as C, statfiles as SF
from .ingest import name_column, parse_md_table, to_num

SEASON_BASE = 2026          # base CSV 의 실제 시즌 (파일명은 2025로 잘못 붙어있음)
POOL_POS = ["FW"]           # 스트라이커 풀. 필요시 ["FW", "FWMF"] 로 확장
MIN_90S = C.MIN_90S_FILTER

PROCESSED = C.DATA_DIR / "processed"

# 스트라이커 레이더 축 = 빠르게 안정되는 '과정' 지표만
RADAR_2026 = [
    ("xg_90", "xG/90"),
    ("Sh_90", "슈팅/90"),
    ("SoT_90", "유효슈팅/90"),
    ("xa_90", "xA/90"),
    ("key_passes_90", "키패스/90"),
    ("dribbles_90", "드리블성공/90"),
]


def _name_map() -> dict[str, str]:
    m = pd.read_csv(C.DATA_DIR / "name_map.csv")
    return dict(zip(m["fotmob_name"], m["player"]))


def _row_goal_assist(r: dict[str, str]) -> tuple[float | None, float | None]:
    """행에서 '실제 득점/도움' 값만. '편차 (득점 - xG)' 같은 파생 컬럼은 제외."""
    g = a = None
    for k, v in r.items():
        if "편차" in k or "xG" in k or "xA" in k:
            continue
        if ("실제 득점" in k) or k.strip() in ("Goals", "골"):
            g = to_num(v)
        if ("실제 도움" in k) or k.strip() in ("Assists", "도움"):
            a = to_num(v)
    return g, a


def _collect_season(season: int, players: set[str], nmap: dict[str, str],
                    report: list[str], ref: pd.DataFrame) -> pd.DataFrame:
    """해당 시즌의 등록된 스탯 파일들을 파싱해 player 기준 wide DataFrame.

    동명이인(예: 2026 K리그1 'Gun-Hee Kim' 2명) 처리: 한 파일에서 같은 이름이 여러 줄이면
    base CSV 의 Gls/Ast 에 가장 가까운 줄을 채택 (골/도움 컬럼이 있을 때). 없으면 첫 줄 + 경고.
    """
    ref_ga = {row.Player: (row.Gls, row.Ast) for row in ref.itertuples()}
    wide: dict[str, dict[str, float]] = {p: {} for p in players}
    files = SF.STAT_FILES.get(season, {})
    for path, colmap in files.items():
        if not Path(path).exists():
            report.append(f"- ⚠ 없음: `{Path(path).name}` (건너뜀)")
            continue
        rows = parse_md_table(path)
        by_player: dict[str, list[dict]] = {}
        for r in rows:
            player = nmap.get(name_column(r))
            if player and player in wide:
                by_player.setdefault(player, []).append(r)

        for player, cands in by_player.items():
            r = cands[0]
            if len(cands) > 1:
                g0, a0 = ref_ga.get(player, (None, None))
                scored = []
                for c in cands:
                    cg, ca = _row_goal_assist(c)
                    if cg is None and ca is None:
                        scored.append((99, c))
                    else:
                        s = abs((cg or 0) - (g0 or 0)) + abs((ca or 0) - (a0 or 0))
                        scored.append((s, c))
                scored.sort(key=lambda x: x[0])
                if scored[0][0] >= 99:
                    # 골/도움 컬럼 없어 특정 불가 → 잘못 넣느니 건너뜀 (NaN 유지)
                    report.append(f"  - 동명이인 `{name_column(r)}` {len(cands)}줄 → {player}: "
                                  f"⚠ 특정 불가, 이 파일 스킵")
                    continue
                r = scored[0][1]
                report.append(f"  - 동명이인 `{name_column(r)}` {len(cands)}줄 → {player}: 골/도움 대조로 선택")
            for src_col, metric in colmap.items():
                if src_col in r:
                    wide[player][metric] = to_num(r[src_col])
        report.append(f"- ✅ `{Path(path).name}` → 풀 매칭 {len(by_player)}/{len(players)}명, 지표 {list(colmap.values())}")

    # 2026 부분 발췌 CSV
    if season == 2026:
        for path, colmap in SF.PARTIAL_CSV_2026.items():
            if not Path(path).exists():
                continue
            df = pd.read_csv(path, comment="#")
            for _, r in df.iterrows():
                player = nmap.get(str(r.get("fotmob_name", "")).strip())
                # xg.csv 는 이름 표기가 base 와 다를 수 있어 fotmob_name 컬럼 사용
                if player is None:
                    # xg.csv 는 base 이름 그대로 쓴 경우도 있음
                    cand = str(r.get("fotmob_name", "")).strip()
                    player = cand if cand in wide else None
                if player is None or player not in wide:
                    continue
                for src_col, metric in colmap.items():
                    if src_col in r and pd.notna(r[src_col]):
                        wide[player].setdefault(metric, float(r[src_col]))
            report.append(f"- ✅ `{path.name}` (부분 발췌) → 지표 {list(colmap.values())}")

    return pd.DataFrame.from_dict(wide, orient="index")


def _reliability(minutes: float) -> str:
    if pd.isna(minutes):
        return "미상"
    if minutes < 900:
        return "낮음(<900분)"
    if minutes < 1800:
        return "중간(900~1800)"
    return "안정(1800+)"


def main() -> int:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    report: list[str] = [f"# 빌드 리포트\n\nbase 시즌: {SEASON_BASE} (파일명 2025는 오기)\n"]

    base = pd.read_csv(C.SCOUTING_CSV)
    base.columns = [c.strip().lstrip("﻿") for c in base.columns]
    pool = base[base["Pos"].isin(POOL_POS) & (base["90s"] >= MIN_90S)].copy()
    pool["age_years"] = pool["Age"].str.slice(0, 2).astype(float)
    players = set(pool["Player"])
    report.append(f"\n## 풀\nPos∈{POOL_POS}, 90s≥{MIN_90S} → **{len(players)}명**\n")

    nmap = _name_map()

    # ---- 2026 ----
    report.append("\n## 2026 스탯 파일")
    s26 = _collect_season(2026, players, nmap, report, pool)
    df = pool.merge(s26, left_on="Player", right_index=True, how="left")

    df["minutes"] = df["90s"] * 90
    df["reliability"] = df["minutes"].map(_reliability)

    # 리더보드는 ~0 인 선수를 아예 안 실음 → 다른 2026 파일에 잡힌 선수는 0 으로 채움
    matched_any = df["xa"].notna() | df["key_passes"].notna() | df["dribbles_90"].notna()
    ZERO_FILL = ["key_passes", "key_passes_90", "big_chances_created",
                 "big_chances_missed", "dribbles_90", "dribble_success_pct", "pk_won"]
    for col in ZERO_FILL:
        if col in df:
            df.loc[matched_any & df[col].isna(), col] = 0.0

    # base CSV 와 교차검증 (같은 시즌이면 거의 일치해야 함)
    report.append("\n### 교차검증 (base CSV vs FotMob 파일)")
    for src, basecol, label in [("assists_src", "Ast", "도움"), ("goals_src", "Gls", "골")]:
        if src in df:
            bad = df.loc[(df[src] - df[basecol]).abs() > 1, ["Player", basecol, src]]
            report.append(f"- {label}: 전부 ±1 이내 ✅" if bad.empty
                          else "\n".join(f"  - ⚠ {t.Player}: base {getattr(t, basecol)} vs 파일 {getattr(t, src)}"
                                         for t in bad.itertuples()))
            df = df.drop(columns=[src])
    if "sot_90_src" in df:
        df = df.drop(columns=["sot_90_src"])
    for tot, per90 in [("xg", "xg_90"), ("xa", "xa_90"),
                       ("big_chances_created", "bcc_90"), ("big_chances_missed", "bcm_90")]:
        if tot in df:
            df[per90] = (df[tot] / df["90s"]).round(3)

    # ---- bio (Transfermarkt 수동) ----
    bio_path = C.DATA_DIR / "collect" / "bio.csv"
    if bio_path.exists():
        bio = pd.read_csv(bio_path)
        keep = [c for c in ["dob", "height_cm", "weight_kg", "preferred_foot", "nationality",
                            "nt_caps", "nt_goals", "market_value_eur", "market_value_asof",
                            "contract_until", "boot_sponsor"] if c in bio.columns]
        df = df.merge(bio[["Player"] + keep], on="Player", how="left")
        if "contract_until" in df:
            today = pd.Timestamp.today().normalize()
            def _yrs_left(v):
                if pd.isna(v) or str(v).strip() in ("", "-"):
                    return None
                s = str(v).strip()
                dt = pd.to_datetime(s, errors="coerce")
                if pd.isna(dt) and s[:4].isdigit():
                    dt = pd.Timestamp(int(s[:4]), 12, 31)   # 연도만 있으면 연말로
                return round((dt - today).days / 365, 2) if pd.notna(dt) else None
            df["contract_years_left"] = df["contract_until"].map(_yrs_left)
        filled = df["dob"].notna().sum() if "dob" in df else 0
        report.append(f"\n### bio.csv\n- 채워진 선수: {filled}/{len(df)}")

    # percentile (풀 내부)
    pct_cols = []
    for col, _ in RADAR_2026:
        if col in df and df[col].notna().sum() >= 3:
            df[f"{col}_pct"] = (df[col].rank(pct=True) * 100).round(1)
            pct_cols.append(col)
    df["radar_ready"] = df[[f"{c}_pct" for c in pct_cols]].notna().all(axis=1) if pct_cols else False

    df.to_csv(PROCESSED / "strikers_2026.csv", index=False, encoding="utf-8-sig")
    report.append(f"\n→ `data/processed/strikers_2026.csv` ({len(df)}행)")
    report.append(f"\n### 2026 지표별 결측")
    for col in ["xg", "xa", "key_passes_90", "dribbles_90", "big_chances_created",
                "big_chances_missed", "fouls_drawn_90", "shot_accuracy_pct"]:
        if col in df:
            miss = df.loc[df[col].isna(), "Player"].tolist()
            report.append(f"- **{col}**: {df[col].notna().sum()}/{len(df)}"
                          + (f" — 결측: {', '.join(miss)}" if miss else ""))
        else:
            report.append(f"- **{col}**: 파일 없음")

    # ---- 2025 (직전 시즌 레이어) ----
    report.append("\n## 2025 스탯 파일 (직전 시즌)")
    s25 = _collect_season(2025, players, nmap, report, pool)
    if not s25.empty:
        s25 = s25.reset_index().rename(columns={"index": "Player"})
        # 2025 출전분 → 90s_2025 → 누적지표 per-90
        if "minutes" in s25:
            s25["nineties_2025"] = (s25["minutes"] / 90).round(1)
            for tot, per90 in [("xg", "xg_90"), ("xa", "xa_90"),
                               ("goals", "goals_90"), ("assists", "assists_90")]:
                if tot in s25:
                    s25[per90] = (s25[tot] / s25["nineties_2025"]).round(3)
            s25["reliability_2025"] = s25["minutes"].map(_reliability)
        # 2025 데이터가 실제로 있는 선수만
        val_cols = [c for c in s25.columns if c not in ("Player",)]
        s25 = s25[s25[val_cols].notna().any(axis=1)].copy()
        # 풀 내부 percentile (2025 표본)
        for col in ["xg_90", "xa_90", "key_passes_90", "dribbles_90", "sot_90"]:
            if col in s25 and s25[col].notna().sum() >= 3:
                s25[f"{col}_pct"] = (s25[col].rank(pct=True) * 100).round(1)
        s25.to_csv(PROCESSED / "strikers_2025.csv", index=False, encoding="utf-8-sig")
        report.append(f"\n→ `data/processed/strikers_2025.csv` — 2025 기록 있는 풀 선수 **{len(s25)}명**")
        report.append(f"  ({', '.join(sorted(s25['Player']))})")
        report.append("\n### 2025 지표별 커버")
        for col in ["minutes", "matches", "goals", "assists", "xg", "xa",
                    "key_passes_90", "sot_90", "dribbles_90"]:
            if col in s25:
                report.append(f"- **{col}**: {s25[col].notna().sum()}/{len(s25)}")
    else:
        report.append("\n2025 레이어: 매칭된 데이터 없음")

    (PROCESSED / "_build_report.md").write_text("\n".join(report), encoding="utf-8")
    print("\n".join(report))
    print(f"\n[완료] {PROCESSED}/ 갱신")
    return 0


if __name__ == "__main__":
    sys.exit(main())
