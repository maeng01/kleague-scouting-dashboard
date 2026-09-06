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
def _load() -> dict:
    """dict 로 반환 — 필드를 추가해도 호출부 unpack 이 안 깨진다
    (Streamlit Cloud 소프트리로드가 옛 캐시를 재사용하면서 튜플 개수 불일치로 죽던 문제)."""
    strikers = data_loader.load_strikers()
    brand = data_loader.load_brand_fit()
    return {
        "strikers": strikers,
        "prior": data_loader.load_strikers_prior(),
        "brand": brand,
        "merged": data_loader.merge(strikers, brand),
        "case_studies": data_loader.load_case_studies(),
        "player_news": data_loader.load_player_news(),
    }


_D = _load()
strikers_df = _D["strikers"]
prior_df = _D["prior"]
brand_df = _D["brand"]
df = _D["merged"]
case_studies = _D["case_studies"]
player_news = _D["player_news"]
PILOT = set(brand_df["player"])

# ---------------------------------------------------------------------------
st.sidebar.title("⚽ K리그 스트라이커 스카우팅")
page = st.sidebar.radio(
    "페이지",
    ["소개 & 사용법", "선수 대시보드", "파일럿 랭킹", "케이스 스터디", "방법론 & 한계"],
)
st.sidebar.markdown("---")
st.sidebar.caption(
    f"**표본**: {C.SEASON_LABEL} 중 `Pos=FW` & 90s≥{C.MIN_90S_FILTER} → **{C.POOL_SIZE}명**. "
    "모든 percentile 은 이 22명 풀 내부 기준."
)
st.sidebar.caption(
    "**시즌 주의**: 파일명은 '2025'지만 골·도움이 FotMob 2026과 일치 → 실제로는 **2026 진행 중** 데이터. "
    f"직전 완료 시즌({C.PRIOR_SEASON_LABEL})은 별도 레이어(14명)로만 비교."
)
st.sidebar.caption(
    "**SNS**: 파일럿(스트라이커 11명)만 수동 수집. 참여율은 공개 IG 있는 8명 **실측**, "
    "나머지는 미수집."
)

_TIER_BADGE = {"안정(1800+)": "🟢", "중간(900~1800)": "🟡", "낮음(<900분)": "🔴", "미상": "⚪"}


def _reliability_note(row: pd.Series) -> None:
    tier = row.get("reliability", "미상")
    if str(tier).startswith("낮음"):
        st.warning(
            f"🔴 **표본 주의** — {row['Player']}는 2026시즌 90분 환산 **{row['90s']}경기**. "
            "과정 지표(xG/90 등)도 오차가 크고 득점률·결정력은 거의 못 믿는 구간. 절대값과 같이 볼 것."
        )


# ===========================================================================
if page == "소개 & 사용법":
    st.title("K리그 스트라이커 스카우팅 & 브랜드 적합도 대시보드")
    st.caption("파일럿 · 스포츠 에이전시 / 브랜드 엔도스먼트 직무 지원용 포트폴리오")

    st.markdown(
        """
### 이게 뭔가요

**"이 스트라이커를 어떻게 관리하고, 어떤 브랜드와 연결할 것인가"** 를 공개 데이터만으로
근거와 함께 정리해 주는 **의사결정 보조 도구**입니다. 예측 모델이 아니라, 현직 스카우트·
에이전트가 "누구와 먼저 대화할지" 좁히고 "어떤 논리로 브랜드를 설득할지" 준비하는 자료입니다.

> 처음에는 ML로 유소년 잠재력을 예측하는 모델로 기획했지만 —
> ① 생존편향 없는 공개 유소년 데이터가 없고, ② 지원 직무가 필요로 하는 건 예측 정확도가
> 아니라 **판단 근거**라서 — 방향을 "판단 보조 도구"로 바꿨습니다. 상용 플랫폼
> (Nielsen Sports·Hookit·Wyscout)을 대체하지 않고, 그 분석 로직을 이해·구현해 봤다는
> 역량 증명으로 만든 프로젝트입니다.

### 이 도구가 답하는 3가지 질문

| 모듈 | 질문 | 어떻게 답하나 |
|---|---|---|
| **① Scouting Snapshot** | 이 선수, 지금 경기력이 어느 수준인가? | 22명 스트라이커 풀 안에서의 percentile. 단, **표본에 빨리 안정되는 '과정' 지표**(슛·xG·키패스 등)만 레이더로 그리고, 득점률처럼 느리게 안정되는 '결과' 지표는 변동성 경고와 함께 따로 표시 |
| **② Brand Fit & Marketability** | SNS·이미지로 볼 때 마케팅 가치가 얼마나, 어떤 업종에 맞나? | 참여율 최대 가중의 Marketability 점수 + 이미지 태그 기반 7개 업종 카테고리 적합도 |
| **③ Agency Recommendation** | 에이전시 관점에서 강점·리스크·전략은? | 경기력 percentile + 신뢰도 + 나이 + 전년 대비 추세 + Marketability → **규칙 기반** 강점/리스크/전략/우선순위(★) + 스폰서 제안서 초안(.docx) |

### 화면 보는 법 — 핵심 용어 6가지

- **percentile (백분위)** : "이 22명 중 상위 몇 %". 90p면 22명 중 2등 수준. **K리그 전체가 아니라 스트라이커 22명 풀 기준**입니다.
- **신뢰도 티어** : 2026 출전 시간 기준. 🟢 안정(1800분 이상) / 🟡 중간(900–1800분) / 🔴 낮음(900분 미만). 지금은 시즌 중반이라 🟢는 4명뿐 — 나머지는 숫자를 조심해서 봐야 합니다.
- **과정 지표 vs 결과 지표** : 슛/90·xG/90·키패스/90은 약 8–12경기면 믿을 만해집니다(과정). 득점/90·결정력(득점−xG)·전환율은 1.5–2시즌은 쌓여야 신호입니다(결과). 그래서 레이더에는 과정 지표만 씁니다.
- **Marketability (0–100)** : `도달×0.25 + 참여율×0.40 + 언론노출×0.20 + 팬덤폭×0.15`. 참여율에 가장 큰 가중치. 팔로워(도달)는 log 스케일로만 반영합니다.
- **참여율** : 최근 게시물 (좋아요+댓글) ÷ 팔로워. 팔로워 티어 추정이 아니라 **직접 집계**해야 의미가 있습니다. 파일럿 8명은 실측값(Marcão 103만·Diogo 등). Lee Hojae는 개인 계정 없음.
- **카테고리 적합도** : 이미지 태그가 '천장'을 정하고, Marketability가 그 천장의 실현 비율(활성화 계수 0.35에서 1.0)을 정합니다. 이미지가 맞아도 활용할 SNS 채널이 약하면 점수가 눌립니다.

### 5분 따라 하기

1. 왼쪽에서 **선수 대시보드** 선택 → 상단 필터(구단·신뢰도·최소 90s)로 후보를 좁힙니다.
2. **선수 선택** 드롭다운에서 이름을 고릅니다. 🔵 표시가 Brand Fit 파일럿(SNS 수집 완료) 선수입니다. 예: **Yago Cariello**.
3. **① 탭** — 레이더가 오른쪽으로 넓으면 기회 창출이 강한 유형. Yago는 xG/90·유효슈팅/90이 90p대인데, 아래 '결과 지표' 표의 결정력(득점−xG)은 마이너스 → "기회는 많이 만드는데 마무리는 표본이 더 필요".
4. **② 탭** — Marketability 막대에서 어느 축이 점수를 끌고/눌렀는지 봅니다. Yago는 참여율 20.7%가 도달(팔로워 9.1K)을 상쇄. 카테고리 표 1위는 '게임·e스포츠'.
5. **③ 탭** — 강점/리스크/전략과 ★ 우선순위. 하단 버튼으로 제안서 초안(.docx)을 받습니다.
6. **케이스 스터디** 페이지에서 각 모듈 설계의 근거가 된 실제 엔도스먼트/스카우팅 사례를 봅니다.

### 데이터 출처

| 레이어 | 소스 | 커버 |
|---|---|---|
| 경기력 기초 (골·도움·슛) | FBref Standard + Shooting (수동 CSV) | 22/22 |
| 고급 지표 (xG·xA·키패스·빅찬스·드리블) | FotMob 리그 리더보드 수동 수집 → `rebuild.py` 파싱 | 21/22 |
| 직전 시즌(2025 완료) 비교 | FotMob | 14/22 (나머지는 2026 신규 영입) |
| 선수 bio (신장·발·시장가치·계약) | Transfermarkt·나무위키 (수동) | 22/22 (일부 필드 비공개) |
| SNS·참여율 | Instagram 공개 게시물 직접 집계 | 파일럿 8명 참여율 실측(+2명 팔로워만) |

자동 스크래핑은 하지 않습니다 — FBref 봇 차단 / K리그 포털 robots.txt / FotMob ToS 모두 금지.
사람이 수집하고, 코드는 파싱·percentile·신뢰도 계산만 합니다. 갱신법은 **방법론 & 한계** 페이지 참고.

### 이 도구가 하지 않는 것

- 계약금 규모 산정 (유사 딜 비교·CPM 벤치마크 필요)
- **브랜드 세이프티** — 도핑·음주운전·계약분쟁·SNS 설화 이력 스크리닝 (실무에선 반드시 별도 검토)
- 팔로워 인구통계 (연령·성별·지역), 콘텐츠 적합도 분석
- ML 잠재력 예측 / 역사적 백테스팅 (향후 확장 로드맵)

자세한 산식·표본 한계는 **방법론 & 한계** 페이지에 있습니다.
"""
    )
    st.info(C.DISCLAIMER)


# ===========================================================================
elif page == "선수 대시보드":
    st.title("선수 상세")

    c1, c2, c3, c4 = st.columns(4)
    squads = ["전체"] + sorted(strikers_df["Squad"].dropna().unique())
    squad = c1.selectbox("구단", squads)
    tiers = ["전체"] + [t for t in C.RELIABILITY_ORDER if t in strikers_df["reliability"].values]
    tier = c2.selectbox("신뢰도 티어", tiers)
    arch_opts = ["전체"] + [a for a in ("타깃형", "기동·연결형", "밸런스형") if a in strikers_df["archetype"].values]
    arch = c3.selectbox("아키타입", arch_opts, help="신장 + 드리블/키패스 기반 대략 분류")
    min_90s = c4.slider("최소 90s", 5.0, float(strikers_df["90s"].max()), 5.0, 0.5)

    view = strikers_df.copy()
    if squad != "전체":
        view = view[view["Squad"] == squad]
    if tier != "전체":
        view = view[view["reliability"] == tier]
    if arch != "전체":
        view = view[view["archetype"] == arch]
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

    _arch = row.get("archetype")
    _arch_txt = f" · {_arch}" if _arch and _arch != "—" else ""
    st.markdown(
        f"### {row['Player']}  \n"
        f"{row['Squad']} · 스트라이커{_arch_txt} · {row['nation_code']} · {row['age_display']} · "
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

    _news = player_news.get(player)
    _items = (_news or {}).get("items", [])
    if len(_items) >= 3:
        with st.expander(f"📰 최근 뉴스 {len(_items)}건  ·  {_news['asof']} 수집", expanded=False):
            st.caption(
                "네이버 뉴스 검색(관련도순) 중 **제목에 선수명이 든 기사**만, 최신순. "
                "스탯이 아니라 맥락 — 득점·부상·이적·대표팀 신호. 수집 시점 스냅샷이라 날짜를 함께 본다."
            )
            for it in _items:
                src = f" · {it['source']}" if it.get("source") else ""
                title = f"[{it['title']}]({it['url']})" if it.get("url") else it["title"]
                st.markdown(f"- `{it['date']}`{src} — {title}")
    elif _news is not None:
        st.caption("📰 최근 뉴스: 제목에 선수명이 직접 언급된 국내 기사가 최근 거의 없음 (팀 소식 위주).")

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
            _m, _min = prow.get("matches"), prow.get("minutes")
            _out = "2025 출전량 미상" if pd.isna(_m) or pd.isna(_min) else f"2025 {int(_m)}경기 {int(_min)}분"
            st.markdown(f"#### 2025 → 2026 추세  ·  {_out}")
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
    st.title("케이스 스터디 — 설계의 근거")
    st.caption(
        "각 모듈의 점수 체계·경고 문구가 왜 그렇게 설계됐는지를, 실제 엔도스먼트·스카우팅 "
        "사례에 붙여 설명합니다. 모듈별로 묶어 봤습니다."
    )
    _MODULE_ORDER = ["① Scouting Snapshot", "② Brand Fit & Marketability", "③ Agency Recommendation"]
    _grouped = {m: [c for c in case_studies if c.get("module") == m] for m in _MODULE_ORDER}
    _ungrouped = [c for c in case_studies if c.get("module") not in _MODULE_ORDER]

    for mod in _MODULE_ORDER:
        items = _grouped[mod]
        if not items:
            continue
        st.markdown(f"## {mod}")
        for cs in items:
            with st.expander(f"{cs['title']}  ·  {cs.get('category','')} ({cs['year']})"):
                st.markdown(f"**핵심 논지 — {cs['thesis']}**")
                st.write(cs["body"])
                st.success(f"이 프로젝트에의 함의 — {cs['takeaway_for_project']}")
                if cs.get("source_note"):
                    st.caption(f"출처 메모: {cs['source_note']}")
    for cs in _ungrouped:
        with st.expander(f"{cs['title']}  ·  {cs.get('category','')} ({cs['year']})"):
            st.markdown(f"**핵심 논지 — {cs['thesis']}**")
            st.write(cs["body"])
            st.success(f"이 프로젝트에의 함의 — {cs['takeaway_for_project']}")
            if cs.get("source_note"):
                st.caption(f"출처 메모: {cs['source_note']}")


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
- **SNS/이미지**: 파일럿(스트라이커 11명)만 수동 수집. 참여율은 공개 IG 있는 **8명 실측**
  (게시물별 좋아요/댓글). 2026-08 로그인 없이 5명(og:description) → 2026-09 Instagram 이
  비로그인 접근을 막아, 로그인 세션(Claude in Chrome)으로 Marcão 추가 + 재검증.
  나머지 파일럿은 공개 개인 계정 미확인.

### 지표를 '과정'과 '결과'로 나눈 이유 — 표본 안정화
모든 지표가 같은 속도로 믿을 만해지지 않는다.

| 종류 | 예 | 신뢰 구간 진입 |
|---|---|---|
| **과정 지표** (반복 행동) | xG/90, 슈팅/90, xA/90, 키패스/90, 드리블/90 | 약 8–12경기 |
| **결과 지표** (드문 이벤트) | 득점/90, 도움/90, 결정력(득점−xG), 전환율 | 1.5–2시즌+ (슈팅 40–50개+) |

→ **레이더·percentile 은 과정 지표만.** 결과 지표는 별도 표에 "참고·변동성 큼"으로 표기.
결정력(xG 대비 초과 득점)은 공개 연구상 대부분 선수에게 한 시즌 내내도 노이즈 — 여러 시즌 필요.

### 신뢰도 티어 (2026 출전분 기준)
🟢 안정(1800분 이상) · 🟡 중간(900–1800분) · 🔴 낮음(900분 미만). 22명 중 15+90s 는 4명뿐, 8경기 미만 8명 →
풀 절반이 "과정 지표는 겨우, 득점률은 거의 못 믿는" 구간. 2025+2026 합산 시 두 시즌 다 뛴 선수는
신뢰도가 올라감 (단, 나이·팀 이동으로 '진짜 실력이 안 변했다'는 가정이 깨질 수 있어 블렌드는 최근 가중).

### ① Scouting Snapshot
Per-90 → 풀 내 percentile → 레이더/막대. 90s·신뢰도 티어 항상 병기. 2025 vs 2026 rate 비교.

**플레이 아키타입** — 신장 + 드리블/90 + 키패스/90 점수 합으로 **타깃형 / 기동·연결형 / 밸런스형** 라벨.
공중볼 데이터가 공개로 없어 신장으로 대체한 근사치라 정밀 분류는 아니고, 후보 좁히기·브랜드 매칭
(타깃형 → 높이 소구 캠페인) 대화용. 선수 선택 위 필터로도 쓴다.

### ② Brand Fit & Marketability
`Marketability = 도달×{C.MARKETABILITY_WEIGHTS['reach']} + 참여율×{C.MARKETABILITY_WEIGHTS['engagement']}
 + 언론노출×{C.MARKETABILITY_WEIGHTS['media']} + 팬덤폭×{C.MARKETABILITY_WEIGHTS['fanbase']}` (참여율 최대 가중).
카테고리 적합도 = 이미지 태그 친화도(천장) × 활성화계수(0.35 + 0.65×marketability/100).
파일럿 11명이 대부분 '외국인 저니맨 스트라이커'라 `global_journey`·`hardworking_pro` 태그가 겹쳐,
같은 카테고리(여행·금융)로 몰리는 경향이 있다. 절대 순위보다 **선수별 상대 순위와 근거 태그**를 보는 게 맞다.
친화도 행렬(`config.BRAND_CATEGORIES`)은 2026-09 파일럿 분포로 한 차례 보정함(gaming 이 기본값 되던 문제).

**참여율 실측 (파일럿 8명)** — IG 게시물별 좋아요(±댓글)/팔로워, 최근 3–10건 평균:
| 선수 | 팔로워 | 참여율 | 메모 |
|---|---|---|---|
| Yago Cariello | 9.1K | **20.7%** | 소규모·고밀도 |
| Bruno Mota | 8.7K | ~15% | 좋아요만(댓글 제한 계정) |
| Stefan Mugoša | 21.7K | 10.5% | |
| Tiago Orobó | 20K | 8.0% | |
| Patryk Klimala | 45.4K | 6.7% | |
| Joo Min-kyu | 29.6K | 3.9%* | 댓글 비활성, 실제론 더 높음 |
| **Marcão** | **1,034K** | **3.2%** | adidas football 계약 · 축구 게시물 좋아요 3.3만 |
| Diogo | 78K | ~1.3% | 78K 치고 낮음 — 비활성 팔로워 추정 |

→ **소규모 계정(9K–45K)에서는 팔로워가 많을수록 참여율이 낮아진다** — Yago·Bruno Mota는 1만 미만에
참여율 15–20%, Klimala는 4.5만에 6.7%. 팬덤이 작고 밀도가 높을수록 반응률이 높다.
→ **Marcão(103만·adidas)는 다른 티어** — 100만 계정에서 3.2%는 이례적으로 높다(대개 1% 미만).
"작지만 밀도 높은 팬덤" 논리가 필요 없는 유일한 선수. 산식이 자동 반영 — 도달(reach) 축 만점이라 점수가 규모에서 나온다.
→ **Diogo(78K·참여율 1.3%)는 반대 경고** — 팔로워는 큰데 반응이 눌린 케이스. 도달만 크고 참여가 낮으면
협찬 전환이 안 나올 수 있어, 참여율 가중이 이런 계정의 Marketability 를 끌어내린다(Diogo 42, Bruno Mota 63).
→ **좋아요 비공개 계정**(Hleihil `abdallahlehel` 1.8만, Vitor Gabriel `v_gabriel09` 16.9만): 팔로워는 확인,
참여율은 계정주만 볼 수 있어 미측정 → Marketability 는 참여율 중립값(40)으로 계산.
→ **Lee Hojae**: 본인 개인 Instagram 없음(팬페이지만) — 도달·참여 축 0, 성장 서사·대표팀 노출로 판단.

**언론 노출(media)** — 1–5 수동 버킷을 **재현 가능한 지표로 교체 완료**(2026-09):
파일럿 11명의 `news_count` = 네이버 뉴스 검색(NAVER API HUB) 고정 질의의 전체 건수(`total`).
`src/brand_fit.py` 가 `log10(news_count)` 를 0–100 으로 매핑해 media 축에 반영한다.
| 선수 | 뉴스 건수 | 선수 | 뉴스 건수 |
|---|---|---|---|
| 주민규 | 38,211 | 마르캉(말컹) | 9,350 |
| 무고사 | 18,654 | 이호재 | 8,744 |
| 모따(Bruno) | 5,662 | 야고 | 4,459 |
| 클리말라 | 2,639 | 디오구 | 862 |
| 페리어 | 821 | 디오고 | 1,326 |
| 오로보·흘레이할 | ~30 (2026 신규·역할 선수, 노출 미미) | | |

질의어·표기 근거는 `data/collect/naver_queries.csv`, 수집 스크립트 `src/collect_naver.py`,
가이드 `data/collect/COLLECT_NAVER.md`. `total` 은 기간 필터가 없어 '최근 폼'이 아니라 '누적 인지도'.

**최근 뉴스 타임라인** (선수 페이지) — 같은 API 로 관련도순 헤드라인을 받아 **제목에 선수명이 든
기사만** 골라 최신 6건 표시. 스탯이 아니라 맥락(득점·부상·이적·대표팀). 이호재 다름슈타트
데뷔골, 디오고 1골1도움, 야고 라운드 MVP 등. 제목 언급이 얇은 선수(무고사·마르캉·페리어·흘레이할)는 미표시 —
"국내 언론에 선수 개인으로는 잘 안 나온다"는 것 자체가 신호. 스탯 추출은 안 함(API 가 본문을 안 줌).

### ③ Agency Recommendation
과정지표 percentile + 신뢰도 티어 + 연령 + 2025 대비 추세 + marketability → 규칙 기반 강점/리스크/전략/★.
ML 예측 아님. 제안서 초안(.docx) 자동 생성.

### 한계
- 표본이 작고 시즌 진행 중 → "파일럿". 라운드 스냅샷임을 명시.
- SNS는 공개 API 제약으로 수작업 수집. 참여율은 파일럿 8명 실측(+2명 팔로워만·1명 계정없음 확인).
- 언론 노출 = 네이버 뉴스 검색 건수(파일럿 11명 실측). 전체 기간 누적이라 '최근 화제성'과는 다름.
  외국인 선수 한글 표기가 미정착이면(오로보·흘레이할) 건수가 실제보다 낮게 잡힘 — `naver_queries.csv` 에 기록.
- Brand Fit 점수는 정성 판단 섞인 반정량 지표 — 예측이 아니라 의사결정 보조.
- **브랜드 세이프티**(도핑·음주운전·계약분쟁·SNS 설화)와 팔로워 인구통계는 범위 밖.
  실무 의사결정에선 반드시 별도 검토 (케이스 스터디 '샤라포바 2016' 참고).
- ML Potential Model·Historical Backtesting 은 향후 확장 로드맵으로만 남김.

---
{C.DISCLAIMER}
""")
