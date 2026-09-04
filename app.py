"""K리그 스트라이커 스카우팅 & 브랜드 적합도 대시보드 (파일럿).

데이터: python rebuild.py 로 생성된 data/processed/*.csv
실행:  streamlit run app.py  (또는 ./run.sh)
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src import agency, brand_fit, config as C, data_loader, proposal, snapshot

st.set_page_config(page_title="K리그 스트라이커 스카우팅", page_icon="⚽", layout="wide")


@st.cache_data
def _load():
    strikers = data_loader.load_strikers()
    prior = data_loader.load_strikers_prior()
    brand = data_loader.load_brand_fit()
    merged = data_loader.merge(strikers, brand)
    return strikers, prior, brand, merged, data_loader.load_case_studies()


strikers_df, prior_df, brand_df, df, case_studies = _load()
PILOT = set(brand_df["player"])

# ---------------------------------------------------------------------------
st.sidebar.title("⚽ K리그 스트라이커 스카우팅")
page = st.sidebar.radio("페이지", ["선수 대시보드", "파일럿 랭킹", "케이스 스터디", "방법론 & 한계"])
st.sidebar.markdown("---")
st.sidebar.caption(
    f"**표본**: {C.SEASON_LABEL} 중 `Pos=FW` & 90s≥{C.MIN_90S_FILTER} → **{C.POOL_SIZE}명**. "
    "모든 percentile 은 이 22명 풀 내부 기준."
)
st.sidebar.caption(
    "**시즌 주의**: 파일명은 '2025'지만 골·도움이 FotMob 2026과 일치 → 실제로는 **2026 진행 중** 데이터. "
    f"직전 완료 시즌({C.PRIOR_SEASON_LABEL})은 별도 레이어(14명)로만 비교."
)
st.sidebar.caption("**SNS**: 파일럿 일부만 수동 수집(2026-08), 참여율은 추정치.")

_TIER_BADGE = {"안정(1800+)": "🟢", "중간(900~1800)": "🟡", "낮음(<900분)": "🔴", "미상": "⚪"}


def _reliability_note(row: pd.Series) -> None:
    tier = row.get("reliability", "미상")
    if str(tier).startswith("낮음"):
        st.warning(
            f"🔴 **표본 주의** — {row['Player']}는 2026시즌 90분 환산 **{row['90s']}경기**. "
            "과정 지표(xG/90 등)도 오차가 크고 득점률·결정력은 거의 못 믿는 구간. 절대값과 같이 볼 것."
        )


# ===========================================================================
if page == "선수 대시보드":
    st.title("선수 상세")

    c1, c2, c3 = st.columns(3)
    squads = ["전체"] + sorted(strikers_df["Squad"].dropna().unique())
    squad = c1.selectbox("구단", squads)
    tiers = ["전체"] + [t for t in C.RELIABILITY_ORDER if t in strikers_df["reliability"].values]
    tier = c2.selectbox("신뢰도 티어", tiers)
    min_90s = c3.slider("최소 90s", 5.0, float(strikers_df["90s"].max()), 5.0, 0.5)

    view = strikers_df.copy()
    if squad != "전체":
        view = view[view["Squad"] == squad]
    if tier != "전체":
        view = view[view["reliability"] == tier]
    view = view[view["90s"] >= min_90s].sort_values("xg_90_pct", ascending=False, na_position="last")
    if view.empty:
        st.info("조건에 맞는 선수가 없습니다.")
        st.stop()

    def _label(p: str) -> str:
        r = strikers_df.loc[strikers_df["Player"] == p].iloc[0]
        return f"{_TIER_BADGE.get(r['reliability'], '')}{' 🔵' if p in PILOT else ''} {p}"

    player = st.selectbox("선수 선택 (🔵 = Brand Fit 파일럿)", view["Player"].tolist(), format_func=_label)
    row = df.loc[df["Player"] == player].iloc[0]
    prow = data_loader.prior_row(prior_df, player)

    st.markdown(
        f"### {row['Player']}  \n"
        f"{row['Squad']} · 스트라이커 · {row['nation_code']} · {row['age_display']} · "
        f"90s **{row['90s']}** ({row['reliability']}) · {int(row['Gls'])}골 {int(row['Ast'])}도움"
    )
    bio_bits = []
    if pd.notna(row.get("height_cm")):
        h = f"{int(row['height_cm'])}cm"
        if pd.notna(row.get("weight_kg")):
            h += f"/{int(row['weight_kg'])}kg"
        bio_bits.append(h)
    if pd.notna(row.get("preferred_foot")):
        _f = {"right": "오른발", "left": "왼발", "both": "양발"}.get(row["preferred_foot"], row["preferred_foot"])
        bio_bits.append(_f)
    if pd.notna(row.get("nt_caps")) and float(row["nt_caps"]) > 0:
        bio_bits.append(f"{row.get('nationality','')} A대표 {int(row['nt_caps'])}경기")
    if pd.notna(row.get("market_value_eur")):
        bio_bits.append(f"시장가치 €{int(row['market_value_eur']/1000)}k")
    if pd.notna(row.get("contract_until")):
        cyl = row.get("contract_years_left")
        bio_bits.append(f"계약 ~{row['contract_until']}" + (f" ({cyl:+.1f}년)" if pd.notna(cyl) else ""))
    if pd.notna(row.get("boot_sponsor")):
        bio_bits.append(f"👟 {row['boot_sponsor']}")
    if bio_bits:
        st.caption(" · ".join(bio_bits) + "  — Transfermarkt (2026-05 기준)")
    _reliability_note(row)

    t1, t2, t3 = st.tabs(["① Scouting Snapshot", "② Brand Fit & Marketability", "③ Agency Recommendation"])

    # ---- ① ----
    with t1:
        st.caption("레이더·막대는 **표본에 빨리 안정되는 '과정' 지표**의 percentile (풀 22명 기준). "
                   "득점률·결정력은 아래에 따로 — 표본에 느리게 안정되는 '결과' 지표.")
        cA, cB = st.columns(2)
        with cA:
            others = ["(비교 없음)"] + [p for p in view["Player"] if p != player]
            cmp_name = st.selectbox("비교 선수", others)
            cmp_row = None if cmp_name == "(비교 없음)" else df.loc[df["Player"] == cmp_name].iloc[0]
            st.plotly_chart(snapshot.radar(row, cmp_row))
        with cB:
            st.plotly_chart(snapshot.percentile_bars(row))

        st.markdown("#### 결과 지표 (참고 — 변동성 큼)")
        oc = []
        for m in C.OUTCOME_METRICS:
            v = row.get(m["key"])
            if pd.notna(v):
                oc.append({"지표": m["label"], "값": f"{float(v):.2f}{m['unit']}"})
        st.dataframe(pd.DataFrame(oc), width="stretch", hide_index=True)
        st.caption("결정력(득점−xG)은 대부분 선수에게 한 시즌으로는 노이즈. 2시즌 이상 누적돼야 신호로 해석 가능.")

        fig = snapshot.season_compare_bars(row, prow)
        if fig is not None:
            st.markdown(f"#### 2025 → 2026 추세  ·  2025 {int(prow['matches'])}경기 {int(prow['minutes'])}분")
            st.plotly_chart(fig)
        else:
            st.caption("2025 완료 시즌 데이터 없음 (2026 신규 영입이거나 직전 시즌 K리그1 미출전).")

    # ---- ② ----
    with t2:
        if pd.isna(row.get("player")):
            st.info(f"{player}는 Brand Fit 파일럿 대상이 아닙니다. '파일럿 랭킹' 페이지 참고.")
        else:
            mkt = brand_fit.marketability(row)
            fits = brand_fit.category_fit(row, mkt)
            m1, m2 = st.columns([1, 2])
            m1.metric("Marketability", f"{mkt.score} / 100", help="도달·참여·언론노출·팬덤폭 가중합")
            m1.caption(f"신뢰도: **{mkt.confidence}**")
            if pd.notna(row.get("followers")):
                m1.caption(f"IG @{row['ig_handle']} · 팔로워 ~{int(row['followers']):,} ({row['followers_confidence']})")
            m2.bar_chart(pd.DataFrame({"구성요소": list(mkt.components), "점수": list(mkt.components.values())})
                         .set_index("구성요소"), horizontal=True)
            for n in mkt.notes:
                st.caption(f"· {n}")
            st.markdown("#### 카테고리별 적합도")
            st.dataframe(pd.DataFrame(
                [{"카테고리": f.label, "적합도": f.score, "근거 태그": ", ".join(f.drivers) or "—"} for f in fits]
            ), width="stretch", hide_index=True)
            st.info(brand_fit.rationale_text(row, mkt, fits))
            if isinstance(row.get("image_tags_list"), list) and row["image_tags_list"]:
                st.caption("이미지 태그: " + ", ".join(C.IMAGE_TAGS.get(t, t) for t in row["image_tags_list"]))
            if pd.notna(row.get("story_note")) and str(row.get("story_note")).strip():
                st.caption(f"스토리 메모: {row['story_note']}")

    # ---- ③ ----
    with t3:
        if pd.isna(row.get("player")):
            st.info("Brand Fit 파일럿 대상 선수만 Agency Recommendation 카드를 생성합니다.")
        else:
            mkt = brand_fit.marketability(row)
            fits = brand_fit.category_fit(row, mkt)
            card = agency.build_card(row, mkt, fits, prow)
            st.markdown(f"## {'★' * card.priority_stars}{'☆' * (5 - card.priority_stars)}  우선순위")
            st.caption(card.priority_reason)
            g1, g2 = st.columns(2)
            g1.markdown("#### ✅ 강점\n" + "\n".join(f"- {s}" for s in card.strengths))
            g2.markdown("#### ⚠ 리스크\n" + "\n".join(f"- {r}" for r in card.risks))
            st.markdown("#### 🎯 추천 전략\n" + "\n".join(f"- {s}" for s in card.strategies))
            st.markdown("---")
            st.download_button(
                "📄 스폰서 제안서 초안 (.docx) 다운로드",
                data=proposal.build_docx(row, mkt, fits, card),
                file_name=f"proposal_{row['Player']}.docx".replace(" ", "_"),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            st.caption(C.DISCLAIMER)


# ===========================================================================
elif page == "파일럿 랭킹":
    st.title("Brand Fit 파일럿 랭킹")
    st.caption("선정: xG/90 등 과정지표 상위 스트라이커 중 공개 프로필 확인 가능한 선수. "
               "이들만 SNS/이미지 수동 수집 → Marketability·Agency 산출.")
    rows = []
    for _, r in df[df["player"].notna()].iterrows():
        mkt = brand_fit.marketability(r)
        fits = brand_fit.category_fit(r, mkt)
        card = agency.build_card(r, mkt, fits, data_loader.prior_row(prior_df, r["Player"]))
        rows.append({
            "선수": r["Player"], "구단": r["Squad"], "나이": r["age_display"],
            "90s": r["90s"], "신뢰도": _TIER_BADGE.get(r["reliability"], ""),
            "과정지표(6축 평균 p)": round(agency._process_score(r), 0),
            "Marketability": mkt.score, "Top 카테고리": fits[0].label,
            "우선순위": "★" * card.priority_stars,
        })
    rank_df = pd.DataFrame(rows).sort_values(["우선순위", "Marketability"], ascending=False)
    st.dataframe(rank_df, width="stretch", hide_index=True)
    st.bar_chart(rank_df.set_index("선수")[["과정지표(6축 평균 p)", "Marketability"]], stack=False, height=360)


# ===========================================================================
elif page == "케이스 스터디":
    st.title("엔도스먼트 케이스 스터디")
    st.caption("점수 체계(팔로워보다 가치관·참여율 우선)의 설득력을 보강하는 실제 사례.")
    for cs in case_studies:
        with st.expander(f"{cs['title']}  ·  {cs['category']} ({cs['year']})"):
            st.markdown(f"**핵심 논지 — {cs['thesis']}**")
            st.write(cs["body"])
            st.success(f"이 프로젝트에의 함의: {cs['takeaway_for_project']}")


# ===========================================================================
else:
    st.title("방법론 & 한계")
    st.markdown(f"""
### 데이터 & 시즌
- **경기력 base**: FBref (Standard + Shooting). 파일명은 `2025`지만 골·도움이 FotMob **2026** 시즌
  수치와 13명 전원 일치 → 실제로는 **2026 진행 중** 스냅샷(약 25R). 프로젝트 문서상 시즌 라벨 정정함.
- **고급 지표**: FotMob 리그 리더보드를 수동 복사 → markdown 표 저장 → `python rebuild.py` 로 파싱·병합.
  자동 스크래핑 안 함 (FBref 봇차단 / K리그 포털 robots.txt / **FotMob ToS가 스크래핑 금지**).
  2026-01 FBref–Opta 계약 종료로 FBref 고급스탯이 삭제된 것도 FotMob 병용 이유.
- **풀**: `Pos=FW` & 90s≥{C.MIN_90S_FILTER} → **{C.POOL_SIZE}명**. 모든 percentile 은 이 풀 내부 순위.
- **직전 시즌 레이어**: {C.PRIOR_SEASON_LABEL} — 14/22명 커버(나머지는 2026 신규 영입). 추세 비교용.
- **SNS/이미지**: 파일럿만 수동 수집(2026-08). 참여율은 공개 SNS 있는 5명에 대해 **실측**
  (IG 게시물별 좋아요/댓글, 최근 5~10건). 나머지는 미확인.

### 지표를 '과정'과 '결과'로 나눈 이유 — 표본 안정화
모든 지표가 같은 속도로 믿을 만해지지 않는다.

| 종류 | 예 | 신뢰 구간 진입 |
|---|---|---|
| **과정 지표** (반복 행동) | xG/90, 슈팅/90, xA/90, 키패스/90, 드리블/90 | 약 8–12경기 |
| **결과 지표** (드문 이벤트) | 득점/90, 도움/90, 결정력(득점−xG), 전환율 | 1.5–2시즌+ (슈팅 40–50개+) |

→ **레이더·percentile 은 과정 지표만.** 결과 지표는 별도 표에 "참고·변동성 큼"으로 표기.
결정력(xG 대비 초과 득점)은 공개 연구상 대부분 선수에게 한 시즌 내내도 노이즈 — 여러 시즌 필요.

### 신뢰도 티어 (2026 출전분 기준)
🟢 안정(1800분+) · 🟡 중간(900~1800) · 🔴 낮음(<900). 22명 중 15+90s 는 4명뿐, 8경기 미만 8명 →
풀 절반이 "과정 지표는 겨우, 득점률은 거의 못 믿는" 구간. 2025+2026 합산 시 두 시즌 다 뛴 선수는
신뢰도가 올라감 (단, 나이·팀 이동으로 '진짜 실력이 안 변했다'는 가정이 깨질 수 있어 블렌드는 최근 가중).

### ① Scouting Snapshot
Per-90 → 풀 내 percentile → 레이더/막대. 90s·신뢰도 티어 항상 병기. 2025 vs 2026 rate 비교.

### ② Brand Fit & Marketability
`Marketability = 도달×{C.MARKETABILITY_WEIGHTS['reach']} + 참여율×{C.MARKETABILITY_WEIGHTS['engagement']}
 + 언론노출×{C.MARKETABILITY_WEIGHTS['media']} + 팬덤폭×{C.MARKETABILITY_WEIGHTS['fanbase']}` (참여율 최대 가중).
카테고리 적합도 = 이미지 태그 친화도(천장) × 활성화계수(0.35 + 0.65×marketability/100).

**참여율 실측 (2026-08, 파일럿 5명)** — IG 게시물별 (좋아요+댓글)/팔로워, 최근 5~10건 평균:
| 선수 | 팔로워 | 참여율 |
|---|---|---|
| Yago Cariello | 9.1K | **20.7%** |
| Stefan Mugoša | 21.7K | 10.5% |
| Tiago Orobó | 20K | 8.0% |
| Patryk Klimala | 45.4K | 6.7% |
| Joo Min-kyu | 29.6K | 3.9%* (댓글 비활성, 실제론 더 높음) |

→ **팔로워가 많을수록 참여율은 낮아진다**: Yago는 Klimala의 1/5 팔로워인데 참여율 3배.
팔로워 수만 보면 놓치는 지점이며, 참여율에 최대 가중치를 두는 이유의 실증.

### ③ Agency Recommendation
과정지표 percentile + 신뢰도 티어 + 연령 + 2025 대비 추세 + marketability → 규칙 기반 강점/리스크/전략/★.
ML 예측 아님. 제안서 초안(.docx) 자동 생성.

### 한계
- 표본이 작고 시즌 진행 중 → "파일럿". 라운드 스냅샷임을 명시.
- SNS/참여율은 공개 API 제약으로 수작업·추정.
- Brand Fit 점수는 정성 판단 섞인 반정량 지표 — 예측이 아니라 의사결정 보조.
- ML Potential Model·Historical Backtesting 은 향후 확장 로드맵으로만 남김.

---
{C.DISCLAIMER}
""")
