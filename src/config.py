"""프로젝트 전역 설정: 지표 라벨, Brand Fit 카테고리·가중치, 임계값.

이 파일에 담긴 숫자(가중치·임계값)는 '정답'이 아니라 도메인 지식 기반의
초기 가설이다. 발표/문서에서는 반드시 그렇게 설명한다.
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# 경로
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

SCOUTING_CSV = DATA_DIR / "kleague_2025_attackers_scouting_index.csv"   # 원본(실제 2026 시즌)
STRIKERS_2026_CSV = DATA_DIR / "processed" / "strikers_2026.csv"
STRIKERS_2025_CSV = DATA_DIR / "processed" / "strikers_2025.csv"
BRAND_FIT_CSV = DATA_DIR / "brand_fit_pilot.csv"
CASE_STUDIES_JSON = DATA_DIR / "case_studies.json"

# base CSV 는 파일명이 '2025'지만 실제로는 2026 시즌 진행 중 스냅샷이다 (골·도움이 FotMob 2026과 일치).
SEASON_LABEL = "2026 K리그1 (진행 중 · FBref 스냅샷)"
PRIOR_SEASON_LABEL = "2025 K리그1 (완료)"
POOL_SIZE = 22  # Pos==FW, 90s>=5
MIN_90S_FILTER = 5

# ---------------------------------------------------------------------------
# ① Scouting Snapshot — 지표 정의
# ---------------------------------------------------------------------------
# key: 처리 CSV 컬럼, pct: percentile rank 컬럼, label, unit, stable: 표본에 빨리 안정되는 '과정' 지표 여부
SNAPSHOT_METRICS = [
    {"key": "xg_90",         "pct": "xg_90_pct",         "label": "xG/90",        "unit": "",  "stable": True},
    {"key": "Sh_90",         "pct": "Sh_90_pct",         "label": "슈팅/90",       "unit": "",  "stable": True},
    {"key": "SoT_90",        "pct": "SoT_90_pct",        "label": "유효슈팅/90",   "unit": "",  "stable": True},
    {"key": "xa_90",         "pct": "xa_90_pct",         "label": "xA/90",        "unit": "",  "stable": True},
    {"key": "key_passes_90", "pct": "key_passes_90_pct", "label": "키패스/90",     "unit": "",  "stable": True},
    {"key": "dribbles_90",   "pct": "dribbles_90_pct",   "label": "드리블성공/90", "unit": "",  "stable": True},
]

# 레이더 축 = 위 6개 '과정' 지표 (percentile 로 그림)
RADAR_METRICS = [m["key"] for m in SNAPSHOT_METRICS]

# 결과 지표 — 표본에 느리게 안정됨. 레이더에 안 넣고 별도 표기 + 변동성 경고와 함께.
OUTCOME_METRICS = [
    {"key": "Gls_90",     "label": "득점/90",            "unit": ""},
    {"key": "Ast_90",     "label": "도움/90",            "unit": ""},
    {"key": "finishing_90", "label": "결정력 (득점−xG)/90", "unit": ""},
    {"key": "SoT_pct",    "label": "유효슈팅%",          "unit": "%"},
    {"key": "shot_accuracy_pct", "label": "슈팅 정확도(FotMob)", "unit": "%"},
    {"key": "dribble_success_pct", "label": "드리블 성공률", "unit": "%"},
    {"key": "big_chances_created", "label": "빅찬스 창출(누적)", "unit": ""},
    {"key": "big_chances_missed",  "label": "빅찬스 놓침(누적)", "unit": ""},
    {"key": "fouls_drawn_90", "label": "피파울/90(부분수집)", "unit": ""},
]

RELIABILITY_ORDER = ["안정(1800+)", "중간(900~1800)", "낮음(<900분)", "미상"]

# ---------------------------------------------------------------------------
# ② Brand Fit & Marketability
# ---------------------------------------------------------------------------
# 이미지/가치관 태그 controlled vocabulary
IMAGE_TAGS = {
    "young_prospect": "젊은 유망주 · 성장 서사",
    "national_team": "국가대표급 인지도",
    "veteran_leader": "베테랑 · 리더십",
    "global_journey": "해외 경험 · 글로벌 서사",
    "family_man": "가정적 이미지",
    "flair_entertainer": "화려한 플레이 · 쇼맨십",
    "hardworking_pro": "성실 · 프로페셔널",
    "underdog_story": "언더독 · 역경 극복",
    "local_hero": "지역 연고 밀착",
}

# Marketability Score 구성 가중치 (합 1.0)
# 제안서 방향: 팔로워 수 자체보다 '참여율'과 '이미지 카테고리'를 우선
MARKETABILITY_WEIGHTS = {
    "reach": 0.25,        # 팔로워 규모 (log scale)
    "engagement": 0.40,   # 참여율 — 핵심
    "media": 0.20,        # 언론 노출 빈도 (1~5 수동 버킷)
    "fanbase": 0.15,      # 팬덤 지리적 폭
}

FANBASE_BREADTH_SCORE = {"domestic": 45, "regional": 70, "international": 95}

# 팔로워 log 정규화 기준점 (파일럿 풀 맥락). 1k→낮음, 100k→높음
FOLLOWER_REF_LOW = 1_000
FOLLOWER_REF_HIGH = 120_000

# 참여율(%) → 0~100 점수 앵커. 파일럿 실측(2026-08) 기준 K리그 선수는 팬덤이 작고 밀도가 높아
# 참여율이 높게 나옴: 주민규 3.9(댓글 비활성)·클리말라 6.7·무고샤 10.5·오로보 8.0·야고 20.7.
ENGAGEMENT_REF_LOW = 2.0
ENGAGEMENT_REF_HIGH = 12.0

# 언론 노출: '고정 질의로 뉴스 검색 결과 건수'를 재현 가능한 지표로 삼는다.
# 권장 소스 = 네이버 뉴스 검색 응답의 `total` (질의: 선수 한국어명, 전체 색인 기준).
#   2026년부터 NAVER API HUB(NCP)에서 발급. 스크립트: src/collect_naver.py, 가이드: data/collect/COLLECT_NAVER.md
# brand_fit_pilot.csv 에 news_count 가 있으면 log 스케일로 media 점수 산출,
# 없으면 기존 media_exposure(1~5 수동 버킷)로 fallback.
NEWS_COUNT_LABEL = "네이버 뉴스 검색 total(전체 기간)"
# 파일럿 11명 실측(2026-09) 분포로 앵커 조정: 27 ~ 38,211건, 중앙값 ~4,500.
NEWS_COUNT_REF_LOW = 40       # 40건 이하 → 0점 (log10 보간). 2026 신규·역할 선수는 실제로 0에 수렴
NEWS_COUNT_REF_HIGH = 50000   # 5만건 이상 → 100점

# ---------------------------------------------------------------------------
# 카테고리별 이미지 태그 친화도 (0~1). 없는 태그는 0.
# baseline 은 marketability 점수가 그대로 반영되는 비율.
# ---------------------------------------------------------------------------
BRAND_CATEGORIES = {
    "sportswear": {
        "label": "스포츠웨어",
        "baseline": 0.45,
        "affinity": {
            "national_team": 1.0, "flair_entertainer": 0.85, "young_prospect": 0.85,
            "hardworking_pro": 0.75, "global_journey": 0.55, "local_hero": 0.45,
        },
    },
    "gaming": {
        # young_prospect·flair_entertainer 가 파일럿에서 가장 흔한 태그라 둘 다 최고치면
        # gaming 이 사실상 기본값이 됨 → 0.85/0.8 로 낮춰 스포츠웨어와 붙게 조정 (2026-09)
        "label": "게임 · e스포츠",
        "baseline": 0.35,
        "affinity": {
            "young_prospect": 0.85, "flair_entertainer": 0.8, "global_journey": 0.6,
            "national_team": 0.45,
        },
    },
    "tech": {
        "label": "테크 · 가전 · 통신",
        "baseline": 0.40,
        "affinity": {
            "hardworking_pro": 0.9, "national_team": 0.8, "global_journey": 0.7,
            "young_prospect": 0.6,
        },
    },
    "finance": {
        "label": "금융 · 보험",
        "baseline": 0.40,
        "affinity": {
            "veteran_leader": 1.0, "hardworking_pro": 0.85, "family_man": 0.8,
            "national_team": 0.7, "local_hero": 0.5,
        },
    },
    "fnb": {
        "label": "식음료 · F&B",
        "baseline": 0.50,
        "affinity": {
            "local_hero": 1.0, "family_man": 0.8, "underdog_story": 0.7,
            "hardworking_pro": 0.6, "national_team": 0.6, "flair_entertainer": 0.5,
        },
    },
    "travel_lifestyle": {
        # global_journey 가 파일럿(외국인 스트라이커) 대부분에게 붙어서, flair 까지 높게 주면
        # 여행이 기본값이 됨. 여행 브랜드의 핵심은 '여정'이지 '쇼맨십'이 아니라 flair 0.8→0.6 (2026-09)
        "label": "여행 · 라이프스타일",
        "baseline": 0.40,
        "affinity": {
            "global_journey": 1.0, "family_man": 0.7, "flair_entertainer": 0.6,
            "young_prospect": 0.5,
        },
    },
    "automotive": {
        "label": "자동차 · 모빌리티",
        "baseline": 0.35,
        "affinity": {
            "veteran_leader": 0.9, "national_team": 0.9, "hardworking_pro": 0.8,
            "family_man": 0.7, "global_journey": 0.5,
        },
    },
}

# ---------------------------------------------------------------------------
# 플레이 아키타입 — 신장 + 드리블/키패스로 대략 분류 (스카우팅 맥락용, 정밀 분류 아님)
#   타깃형: 장신·공중 초점, 볼 안 끌고 마무리 / 기동·연결형: 볼 운반·연결 / 밸런스형: 그 사이
# ---------------------------------------------------------------------------
ARCHETYPE_TARGET_MIN = 2       # 점수 합 이 값 이상 → 타깃형
ARCHETYPE_MOBILE_MAX = -1      # 이 값 이하 → 기동·연결형

# ---------------------------------------------------------------------------
# ③ Agency Recommendation — 임계값
# ---------------------------------------------------------------------------
STRENGTH_PCT_THRESHOLD = 75    # percentile rank 이 값 이상이면 강점
RISK_PCT_THRESHOLD = 25        # 이 값 이하이면 약점
SMALL_SAMPLE_90S = 8.0         # 90s 가 이 값 미만이면 표본 경고
VETERAN_AGE = 31              # 이 나이 이상이면 계약기간/리세일 리스크 언급
YOUNG_AGE = 24                # 이 나이 이하 + 생산성 상위면 장기계약 후보

DISCLAIMER = (
    "본 도구는 상용 스카우팅·엔도스먼트 분석 플랫폼(Nielsen Sports, Hookit, Wyscout 등)을 "
    "대체하지 않습니다. 업계 표준 분석 로직을 직접 구현해 이해도를 보이는 학습·역량 증명용 "
    "파일럿이며, 표본(2026 K리그1 스트라이커 22명, 90s≥5 · 시즌 진행 중)과 수작업 SNS 수집의 "
    "한계를 전제로 합니다."
)
