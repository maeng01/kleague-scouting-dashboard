"""수집한 스탯 리포트(.md 표) → 정규 지표 매핑 설정.

파일은 `2026 Stats/` `2025 Stats/` 에 그대로 두고, 여기에 '어느 컬럼이 어느 지표인지'만 등록한다.
사용자가 새 파일을 올리면 이 딕셔너리에 한 줄 추가 → `python -m src.build` 재실행.
"""

from __future__ import annotations

from pathlib import Path

from . import config as C

STATS_2026 = C.ROOT / "2026 Stats"
STATS_2025 = C.ROOT / "2025 Stats"

# season: 파일 경로 → {표의 원본 컬럼명: 정규 지표명}
# 정규 지표명 규칙: _90 접미사 = 90분당, _pct = 퍼센트, 나머지는 시즌 누적
STAT_FILES: dict[int, dict[Path, dict[str, str]]] = {
    2026: {
        STATS_2026 / "kleague1_2026_xa_player_stats.md": {
            "실제 도움 (Assists)": "assists_src",   # base CSV Ast 와 교차검증용
            "예상 어시스트 (xA)": "xa",
        },
        STATS_2026 / "kleague1_2026_chances_created_stats.md": {
            "총 기회 창출 (Total)": "key_passes",
            "90분당 기회 창출 (P90)": "key_passes_90",
        },
        STATS_2026 / "kleague1_2026_big_chances_created_stats.md": {
            "큰 기회 만듦 (BCC)": "big_chances_created",
        },
        STATS_2026 / "kleague1_2026_big_chances_missed_stats.md": {
            "큰 기회 놓침 (BCM)": "big_chances_missed",
            "슈팅 전환율 (%)": "shot_conversion_pct",
        },
        STATS_2026 / "kleague1_2026_shots_on_target_per90_stats.md": {
            "90분당 유효 슈팅 (P90)": "sot_90_src",   # base CSV SoT_90 와 교차검증
            "유효 슈팅 정확도 (%)": "shot_accuracy_pct",
        },
        STATS_2026 / "kleague1_2026_dribbles_completed_per90_stats.md": {
            "90분당 드리블 성공 (P90)": "dribbles_90",
            "드리블 성공률 (%)": "dribble_success_pct",
        },
        STATS_2026 / "kleague1_2026_penalties_won_fouls_drawn_stats.md": {
            "페널티킥 획득 (PK Won)": "pk_won",
            "90분당 피파울 (P90)": "fouls_drawn_90",
        },
        STATS_2026 / "kleague1_2026_xg_player_stats.md": {
            "실제 득점 (Goals)": "goals_src",   # base CSV Gls 교차검증
            "예상 골 (xG)": "xg",               # 누적. xg_90 은 90s 로 계산
        },
    },
    2025: {
        STATS_2025 / "kleague1_2025_xg_player_stats.md": {
            "실제 득점 (Goals)": "goals",
            "예상 골 (xG)": "xg",
        },
        STATS_2025 / "kleague1_2025_xa_player_stats.md": {
            "실제 도움 (Assists)": "assists",
            "예상 어시스트 (xA)": "xa",
        },
        STATS_2025 / "kleague1_2025_chances_created_stats.md": {
            "총 기회 창출 (Total)": "key_passes",
            "90분당 기회 창출 (P90)": "key_passes_90",
        },
        STATS_2025 / "kleague1_2025_minutes_played_stats.md": {
            "총 경기 (Matches)": "matches",
            "총 출전 시간 (Minutes)": "minutes",
        },
        STATS_2025 / "kleague1_2025_shots_on_target_per90_stats.md": {
            "90분당 유효 슈팅 (P90)": "sot_90",
            "유효 슈팅 정확도 (%)": "shot_accuracy_pct",
        },
        STATS_2025 / "kleague1_2025_dribbles_completed_per90_stats.md": {
            "90분당 드리블 성공 (P90)": "dribbles_90",
            "드리블 성공률 (%)": "dribble_success_pct",
        },
        # 중복 업로드 무시: kleague1_2025_assists_xa_player_stats.md (= kleague1_2025_xa_player_stats.md)
    },
}

# 부분 발췌 CSV (raw 파일 대신 임시)
PARTIAL_CSV_2026 = {
    C.DATA_DIR / "collect" / "fotmob_2026" / "xg.csv": {
        "xg_2026": "xg",  # 헤더가 fotmob_name,goals_2026,xg_2026
    },
}
