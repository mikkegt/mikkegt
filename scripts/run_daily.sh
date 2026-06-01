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
  --theme pixel_sweets

# 差分が無ければコミットしない
git add data/ai-usage.json images/ai-usage.svg
if git diff --cached --quiet; then
  echo "no changes"
  exit 0
fi

git -c user.name="ai-usage-bot" \
    -c user.email="kawano.misato+aiusage@gmail.com" \
    commit -m "chore: update AI usage stats"

# リモートが自動コミット(3D contrib)で先行しているのが日常なので、
# push 前に必ず取り込む。ff-only が無理なら merge --no-ff (rebase/force は禁止)。
for attempt in 1 2 3; do
  git fetch origin main
  git merge --ff-only origin/main 2>/dev/null \
    || git merge --no-ff origin/main -m "merge: integrate origin updates"
  if git push origin main; then
    exit 0
  fi
  echo "push attempt $attempt failed, retrying..." >&2
done
echo "push failed after retries" >&2
exit 1
