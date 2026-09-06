"""② Brand Fit & Marketability — 반정량 점수 산출.

핵심 원칙(제안서):
- 팔로워 수 자체보다 참여율(engagement)과 이미지/가치관 카테고리를 우선한다.
- 점수는 예측이 아니라 '판단 보조'. 태깅 근거를 함께 반환해 투명하게 보여준다.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import pandas as pd

from . import config as C


@dataclass
class Marketability:
    score: float
    components: dict[str, float]
    confidence: str          # "낮음" / "보통" / "제한적(SNS 미확인)"
    notes: list[str] = field(default_factory=list)


@dataclass
class CategoryFit:
    key: str
    label: str
    score: float
    drivers: list[str]       # 점수에 기여한 태그 라벨


def _lin(value: float, lo: float, hi: float) -> float:
    """value 를 [lo, hi] → [0, 100] 선형 매핑 후 clip."""
    if hi == lo:
        return 0.0
    return max(0.0, min(100.0, (value - lo) / (hi - lo) * 100))


def _reach_score(followers) -> float:
    if pd.isna(followers) or followers <= 0:
        return 0.0
    lo = math.log10(C.FOLLOWER_REF_LOW)
    hi = math.log10(C.FOLLOWER_REF_HIGH)
    return _lin(math.log10(float(followers)), lo, hi)


def marketability(row: pd.Series) -> Marketability:
    """brand_fit_pilot 한 행(merge 된 Series) → Marketability."""
    followers = row.get("followers")
    eng = row.get("engagement_rate_pct")
    media = row.get("media_exposure")
    breadth = row.get("fanbase_breadth")

    has_sns = pd.notna(followers)
    notes: list[str] = []

    reach = _reach_score(followers)
    if pd.isna(eng):
        engagement = 40.0 if has_sns else 0.0
        if has_sns:
            notes.append("참여율 미수집 → 중립값(40) 대입. 실제 분석 시 최근 게시물 10건의 (좋아요+댓글)/팔로워로 대체.")
    else:
        engagement = _lin(float(eng), C.ENGAGEMENT_REF_LOW, C.ENGAGEMENT_REF_HIGH)
        ec = str(row.get("engagement_confidence"))
        if ec == "rough_estimate":
            notes.append(f"참여율 {eng:g}%는 팔로워 티어 기반 러프 추정치 (직접 카운트 아님).")
        elif ec == "measured_likes_only":
            notes.append(f"참여율 {eng:g}% = 최근 게시물 좋아요만 집계(댓글 미포함)/팔로워 → 실제 참여율은 이보다 높음.")
        elif ec == "measured":
            notes.append(f"참여율 {eng:g}% = 최근 게시물 (좋아요+댓글)/팔로워 실측.")

    news_count = row.get("news_count")
    if pd.notna(news_count) and float(news_count) > 0:
        lo = math.log10(C.NEWS_COUNT_REF_LOW)
        hi = math.log10(C.NEWS_COUNT_REF_HIGH)
        media_score = _lin(math.log10(float(news_count)), lo, hi)
        notes.append(
            f"언론 노출 = {C.NEWS_COUNT_LABEL} {int(float(news_count)):,}건 (log 스케일)."
        )
    elif pd.notna(media):
        media_score = _lin(float(media), 1, 5)
        notes.append("언론 노출 = 1~5 수동 버킷 (재현 가능한 뉴스 건수로 대체 예정).")
    else:
        media_score = 30.0
    fanbase_score = C.FANBASE_BREADTH_SCORE.get(str(breadth), 45.0)

    w = C.MARKETABILITY_WEIGHTS
    total = (
        reach * w["reach"]
        + engagement * w["engagement"]
        + media_score * w["media"]
        + fanbase_score * w["fanbase"]
    )

    if not has_sns:
        # SNS 미확인이면 reach/engagement 축이 비어 점수가 구조적으로 눌림 → 명시
        confidence = "제한적(SNS 미확인)"
        notes.append("공개 개인 SNS를 특정하지 못해 도달·참여 축이 0으로 처리됨. 점수를 절대 비교에 쓰지 말 것.")
    elif str(row.get("engagement_confidence")).startswith("measured"):
        confidence = "높음(참여율 실측)"
    elif str(row.get("followers_confidence")) == "verified":
        confidence = "보통"
    else:
        confidence = "낮음"
        notes.append("팔로워 수가 검색 스니펫 기반으로 미검증.")

    return Marketability(
        score=round(total, 1),
        components={
            "도달(팔로워)": round(reach, 1),
            "참여율": round(engagement, 1),
            "언론 노출": round(media_score, 1),
            "팬덤 폭": round(fanbase_score, 1),
        },
        confidence=confidence,
        notes=notes,
    )


def category_fit(row: pd.Series, mkt: Marketability) -> list[CategoryFit]:
    """이미지 태그 + marketability 로 카테고리별 적합도(0~100)."""
    tags = row.get("image_tags_list")
    if not isinstance(tags, list):
        tags = []

    # 활성화 계수: 이미지 적합도가 '천장'이면 marketability 가 그 천장의 실현 비율을 정한다.
    # SNS 미확인/낮은 marketability 선수는 이미지가 맞아도 활용할 채널이 약함 → 점수가 눌림.
    activation = 0.35 + 0.65 * (mkt.score / 100)

    out: list[CategoryFit] = []
    for key, cfg in C.BRAND_CATEGORIES.items():
        aff = cfg["affinity"]
        matched = [(t, aff[t]) for t in tags if t in aff]
        if matched:
            top = sorted((v for _, v in matched), reverse=True)[:3]
            tag_ceiling = sum(top) / len(top) * 100
        else:
            # 태그 미부여 → 이미지 적합도 불명, 카테고리 baseline 을 중립 천장으로
            tag_ceiling = cfg["baseline"] * 100

        score = tag_ceiling * activation

        drivers = [C.IMAGE_TAGS[t] for t, _ in sorted(matched, key=lambda x: -x[1])]
        out.append(
            CategoryFit(
                key=key,
                label=cfg["label"],
                score=round(min(100.0, score), 1),
                drivers=drivers,
            )
        )

    out.sort(key=lambda c: c.score, reverse=True)
    return out


def rationale_text(row: pd.Series, mkt: Marketability, fits: list[CategoryFit]) -> str:
    """상위 카테고리 근거를 한 문단 텍스트로."""
    top = fits[0]
    drivers = ", ".join(top.drivers) if top.drivers else "이미지 태그 미부여(marketability 기반)"
    return (
        f"marketability {mkt.score}점(신뢰도 {mkt.confidence}) 기준, "
        f"가장 적합한 카테고리는 '{top.label}'({top.score}점). "
        f"근거 태그: {drivers}."
    )
