#!/usr/bin/env zsh
# 日次集計 → SVG/JSON 更新 → git commit & push
# launchd から呼ばれる前提。失敗時は exit code を返す。

set -euo pipefail

REPO_DIR="${REPO_DIR:-$HOME/workspace/github.com/mikkegt/mikkegt}"
PROJECTS_DIR="${PROJECTS_DIR:-$HOME/.claude/projects}"
WINDOW_DAYS="${WINDOW_DAYS:-30}"

cd "$REPO_DIR"

git pull --ff-only origin main || true

python3 scripts/aggregate_ai_usage.py \
  --projects-dir "$PROJECTS_DIR" \
  --json-out data/ai-usage.json \
  --svg-out images/ai-usage.svg \
  --days "$WINDOW_DAYS" \
  --theme dark

python3 scripts/aggregate_ai_usage.py \
  --projects-dir "$PROJECTS_DIR" \
  --json-out data/ai-usage.json \
  --svg-out images/ai-usage-cute.svg \
  --days "$WINDOW_DAYS" \
  --theme cute

# 差分が無ければコミットしない
git add data/ai-usage.json images/ai-usage.svg images/ai-usage-cute.svg
if git diff --cached --quiet; then
  echo "no changes"
  exit 0
fi

git -c user.name="ai-usage-bot" \
    -c user.email="kawano.misato+aiusage@gmail.com" \
    commit -m "chore: update AI usage stats"
git push origin main
