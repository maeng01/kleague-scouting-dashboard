"""
K리그1 선수 데이터 수집 스크립트 (로컬 실행용)

사전 준비:
    pip install soccerdata pandas

실행:
    python kleague_scout_data.py
"""

import soccerdata as sd
import pandas as pd

SEASON = "2025"  # 확인하려는 시즌. 필요시 바꾸세요.

def main():
    candidate_names = [
        "KOR-K League 1",
        "KOR-K-League-1",
        "K League 1",
    ]

    fbref = None
    for name in candidate_names:
        try:
            fbref = sd.FBref(leagues=name, seasons=SEASON)
            print(f"[성공] 리그명 '{name}'으로 연결됨")
            break
        except Exception as e:
            print(f"[실패] '{name}' 시도 → {e}")

    if fbref is None:
        print("\n기본 지원 리그명으로는 안 됩니다.")
        print("→ soccerdata의 'custom leagues' 기능으로 FBref competition ID 55를 직접 등록해야 합니다.")
        print("→ 가이드: https://soccerdata.readthedocs.io/en/latest/howto/custom-leagues.html")
        return

    print("\n선수 시즌 스탯(standard) 수집 중...")
    standard = fbref.read_player_season_stats(stat_type="standard")
    standard.to_csv("kleague_standard_stats.csv", encoding="utf-8-sig")
    print(f"→ 저장 완료: kleague_standard_stats.csv ({len(standard)} rows)")
    print(standard.head())

    print("\n슈팅 스탯(shooting) 수집 중...")
    try:
        shooting = fbref.read_player_season_stats(stat_type="shooting")
        shooting.to_csv("kleague_shooting_stats.csv", encoding="utf-8-sig")
        print(f"→ 저장 완료: kleague_shooting_stats.csv ({len(shooting)} rows)")
    except Exception as e:
        print(f"[실패] shooting 스탯: {e}")

    for stat_type in ["passing", "possession", "gca", "defense"]:
        print(f"\n{stat_type} 스탯 수집 중...")
        try:
            df = fbref.read_player_season_stats(stat_type=stat_type)
            df.to_csv(f"kleague_{stat_type}_stats.csv", encoding="utf-8-sig")
            print(f"→ 저장 완료: kleague_{stat_type}_stats.csv ({len(df)} rows)")
        except Exception as e:
            print(f"[실패] {stat_type} 스탯: {e}")

    print("\n모든 수집이 끝났습니다. 실제로 몇 명의 선수 데이터가 모였는지,")
    print("포지션(pos 컬럼)에 FW/MF가 몇 명인지 CSV를 열어서 직접 확인해보세요.")


if __name__ == "__main__":
    main()
