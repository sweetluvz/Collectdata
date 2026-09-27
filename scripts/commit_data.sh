#!/usr/bin/env bash
# Usage: commit_data.sh <domain> <commit message>
# Rebuilds data/<domain>/CATALOG.md, commits data/<domain> only, and pushes. Each workflow owns one
# domain directory, so rebasing onto concurrent pushes from the other workflows never conflicts.
set -euo pipefail

domain="$1"
msg="$2"
branch="${GITHUB_REF_NAME:?}"

python scripts/build_catalog.py "$domain"

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add "data/$domain"
if git diff --cached --quiet; then
  echo "No new data to commit"
  exit 0
fi
git commit -q -m "$msg"

for attempt in 1 2 3 4 5; do
  if git pull -q --rebase --autostash origin "$branch" && git push -q origin "HEAD:$branch"; then
    echo "Pushed on attempt $attempt"
    exit 0
  fi
  git rebase --abort 2>/dev/null || true
  sleep $((attempt * 10))
done
echo "::error::push failed after 5 attempts"
exit 1
