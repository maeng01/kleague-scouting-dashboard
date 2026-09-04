"""③ Agency Recommendation — 규칙 기반 카드 생성.

Scouting Snapshot(과정지표 percentile · 신뢰도 티어 · 2025 대비 추세) + Brand Fit 을 결합해
강점 / 리스크 / 추천 전략 / 우선순위(★). ML 예측이 아니라 도메인 규칙이다.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from . import config as C
from .brand_fit import CategoryFit, Marketability


@dataclass
class AgencyCard:
    player: str
    priority_stars: int
    priority_reason: str
    strengths: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    strategies: list[str] = field(default_factory=list)
    headline_categories: list[str] = field(default_factory=list)


def _process_score(row: pd.Series) -> float:
    """과정지표 6축 percentile 평균 (온피치 종합 대용, 표본에 빨리 안정되는 값)."""
    vals = [row.get(m["pct"]) for m in C.SNAPSHOT_METRICS]
    vals = [float(v) for v in vals if pd.notna(v)]
    return sum(vals) / len(vals) if vals else 30.0


def build_card(row: pd.Series, mkt: Marketability, fits: list[CategoryFit],
               prior: pd.Series | None = None) -> AgencyCard:
    player = str(row["Player"])
    age = row.get("age_years")
    nineties = float(row.get("90s", 0) or 0)
    tier = str(row.get("reliability", "미상"))
    tags = row.get("image_tags_list") if isinstance(row.get("image_tags_list"), list) else []

    strengths, risks, strategies = [], [], []

    # ---- 강점: 과정지표 상위 --------------------------------------------
    for m in C.SNAPSHOT_METRICS:
        p = row.get(m["pct"])
        if pd.notna(p) and p >= C.STRENGTH_PCT_THRESHOLD:
            strengths.append(f"{m['label']} 스트라이커 풀 상위권 ({p:.0f}p)")

    fin = row.get("finishing_90")
    if pd.notna(fin) and fin >= 0.15 and nineties >= C.SMALL_SAMPLE_90S:
        strengths.append(f"xG 대비 실득점 초과 (+{fin:.2f}/90) — 다만 결정력은 2시즌 이상 봐야 확정")

    if prior is not None:
        for key, k25, lab in [("xg_90", "xg_90", "xG/90"), ("xa_90", "xa_90", "xA/90")]:
            v26, v25 = row.get(key), prior.get(k25)
            if pd.notna(v26) and pd.notna(v25) and v25 > 0.05:
                chg = (v26 - v25) / v25
                if chg >= 0.2:
                    strengths.append(f"{lab} 전년 대비 상승 ({v25:.2f}→{v26:.2f})")
                elif chg <= -0.25:
                    risks.append(f"{lab} 전년 대비 하락 ({v25:.2f}→{v26:.2f})")

    # ---- 강점: 마케팅 -------------------------------------------------
    if mkt.confidence != "제한적(SNS 미확인)" and mkt.score >= 55:
        strengths.append(f"SNS 도달·참여 양호 (marketability {mkt.score})")
    sponsors = row.get("existing_sponsors")
    if pd.notna(sponsors) and str(sponsors).strip():
        strengths.append(f"기존 스폰서 보유: {str(sponsors).strip()}")
    boot = row.get("boot_sponsor")
    if pd.notna(boot) and str(boot).strip():
        strengths.append(f"축구화 계약: {str(boot).strip()} — 스포츠웨어 접점 이미 있음")
    h = row.get("height_cm")
    if pd.notna(h) and float(h) >= 191:
        strengths.append(f"신장 {int(h)}cm — 타깃형 자원 (세트피스·공중 위협)")
    nc = row.get("nt_caps")
    nat = row.get("nationality")
    if pd.notna(nc) and float(nc) >= 10:
        strengths.append(f"{nat} A대표 {int(nc)}경기 — 대표팀 노출 활용 캠페인 레버리지")
    elif pd.notna(nc) and float(nc) >= 1:
        strengths.append(f"{nat} 대표팀 소집 이력 ({int(nc)}경기) — 성장 시 마케팅 상방")
    elif "national_team" in tags:
        strengths.append("국가대표급 인지도 — 캠페인 노출 레버리지")
    if "young_prospect" in tags:
        strengths.append("성장 서사 — 가치 상승 여지")

    # ---- 리스크 ----------------------------------------------------
    if tier.startswith("낮음") or (nineties and nineties < C.SMALL_SAMPLE_90S):
        risks.append(f"표본 작음: 2026시즌 90분 환산 {nineties:g}경기 ({tier}) — "
                     "percentile·결정력 해석에 주의, 절대값과 함께 볼 것")
    if pd.notna(age) and age >= C.VETERAN_AGE:
        risks.append(f"연령 {int(age)}세 — 장기계약·리세일 밸류 제한, 커리어 후반 설계 필요")
    cyl = row.get("contract_years_left")
    if pd.notna(cyl) and cyl <= 0.6:
        mo = max(0, round(cyl * 12))
        risks.append(f"계약 만료 임박 (약 {mo}개월 · {row.get('contract_until')}) — 재계약/이적 협상 즉시 착수")
    mv = row.get("market_value_eur")
    if pd.notna(mv) and float(mv) <= 250000 and _process_score(row) >= 55:
        risks.append(f"시장가치 €{int(mv/1000)}k로 저평가 대비 경기 기여 양호 — 조기 재계약으로 가치 고정 검토")
    if mkt.confidence == "제한적(SNS 미확인)":
        risks.append("공개 SNS 미확인 — 콘텐츠 자산·팬 커뮤니케이션 채널부터 구축해야 함")
    elif mkt.score < 40:
        risks.append("퍼블릭 프로필 약함 — 브랜드 제안 전에 SNS 활성화 선행 필요")

    sh_p, xg_p = row.get("Sh_90_pct"), row.get("xg_90_pct")
    if pd.notna(sh_p) and pd.notna(xg_p) and sh_p - xg_p >= 35:
        risks.append("슈팅량 대비 xG(슈팅 질) 낮음 — 슈팅 선택 개선 여지")
    if pd.notna(fin) and fin <= -0.15 and nineties >= C.SMALL_SAMPLE_90S:
        risks.append(f"xG 대비 실득점 부족 ({fin:.2f}/90) — 불운/결정력 구분에 추가 표본 필요")
    for m in C.SNAPSHOT_METRICS:
        p = row.get(m["pct"])
        if pd.notna(p) and p <= C.RISK_PCT_THRESHOLD and m["key"] in ("xg_90", "xa_90"):
            risks.append(f"{m['label']} 풀 하위권 ({p:.0f}p)")

    # ---- 전략 ----------------------------------------------------
    proc = _process_score(row)
    if pd.notna(age) and age <= C.YOUNG_AGE and proc >= 60:
        strategies.append("장기계약 우선 검토 + 유럽/2부·중동·J리그 이적 시장 모니터링")
    elif pd.notna(age) and age <= 30:
        strategies.append("3~4년 계약으로 전성기 구간 가치 극대화")
    else:
        strategies.append("단기계약 + 은퇴 후 전환(지도자·해설·클럽 앰버서더) 로드맵 병행")

    if tier.startswith("낮음"):
        strategies.append("다음 5–10경기 지표 추이 확인 후 계약 조건 재협상 트리거 설정")
    if mkt.confidence == "제한적(SNS 미확인)" or mkt.score < 50:
        strategies.append("개인 SNS 채널 개설·정비 → 훈련 루틴·비하인드·팬 Q&A 정기 콘텐츠")
    else:
        strategies.append("숏폼(득점 장면·매치데이 브이로그) 강화로 참여율 방어")

    strong_fits = [f for f in fits if f.score >= 45][:2]
    top_fits = strong_fits or fits[:1]
    if strong_fits:
        for f in strong_fits:
            strategies.append(f"'{f.label}' 카테고리 스폰서 우선 접촉 (적합도 {f.score})")
    else:
        strategies.append(f"카테고리 적합도 전반 낮음(최고 {fits[0].label} {fits[0].score}) "
                          "— 타겟팅보다 프로필·콘텐츠 구축 선행")
    if "national_team" in tags or (pd.notna(nc) and float(nc) >= 5):
        strategies.append("대표팀 소집·국제대회 일정에 맞춘 브랜드 캠페인 타이밍 조율")
    if "global_journey" in tags:
        strategies.append("출신국/이전 소속 리그 시장 겨냥한 이중 언어 콘텐츠")

    stars, reason = _priority(proc, mkt, age, tier)

    return AgencyCard(
        player=player, priority_stars=stars, priority_reason=reason,
        strengths=strengths or ["뚜렷한 상위권 지표 없음 — 역할·맥락 기반 재평가 권장"],
        risks=risks or ["구조적 리스크 특이사항 없음"],
        strategies=strategies,
        headline_categories=[f.label for f in top_fits],
    )


def _priority(proc: float, mkt: Marketability, age, tier: str) -> tuple[int, str]:
    market = mkt.score if mkt.confidence != "제한적(SNS 미확인)" else 25.0
    age_bonus = 0.0
    if pd.notna(age):
        age_bonus = 15 if age <= 23 else 8 if age <= 27 else -10 if age >= 33 else 0
    composite = proc * 0.5 + market * 0.35 + 50 * 0.15 + age_bonus
    pen = ""
    if tier.startswith("낮음"):
        composite -= 12
        pen = " (표본 작아 하향)"
    if mkt.confidence == "제한적(SNS 미확인)":
        composite -= 6
    stars = (5 if composite >= 78 else 4 if composite >= 64 else 3 if composite >= 50
             else 2 if composite >= 38 else 1)
    return stars, (f"과정지표 {proc:.0f}p · 마케팅 {market:.0f} · 연령보정 {age_bonus:+.0f} "
                   f"→ 종합 {composite:.0f}{pen}")
