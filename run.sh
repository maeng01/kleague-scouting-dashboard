#!/usr/bin/env bash
# K리그 스카우팅 대시보드 실행
set -e
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
fi
exec .venv/bin/streamlit run app.py
