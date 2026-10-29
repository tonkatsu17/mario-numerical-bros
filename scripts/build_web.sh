#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python scripts/prepare_web.py
python -m pygbag --build web
mkdir -p public
cp -a web/build/web/. public/
echo 'Static site ready in public/'
