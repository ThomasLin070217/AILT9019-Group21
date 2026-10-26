#!/bin/zsh
set -eu
cd -- "$(dirname -- "$0")"
if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv
fi
.venv/bin/python -m pip install -r requirements.txt
print 'Open http://127.0.0.1:8020/app/?mode=local&map=local'
.venv/bin/python serve.py --port 8020
