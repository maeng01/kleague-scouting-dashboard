#!/usr/bin/env python3
"""수집 파일 → 처리 데이터셋 재생성 (옵션 B 파이프라인의 진입점).

워크플로:
  1. FotMob 리그 리더보드를 복사해 `2026 Stats/` 또는 `2025 Stats/` 에 .md 로 저장
     (형식은 기존 파일과 동일한 markdown 표. 새 지표면 src/statfiles.py 에 컬럼 매핑 한 줄 추가)
  2. `python rebuild.py`  ← percentile·신뢰도 티어까지 전부 재계산
  3. `./run.sh` 로 대시보드 확인 (앱은 data/processed/ 를 읽음)

출력: data/processed/strikers_2026.csv, strikers_2025.csv, _build_report.md
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from src.build import main

if __name__ == "__main__":
    sys.exit(main())
