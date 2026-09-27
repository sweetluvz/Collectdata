#!/usr/bin/env bash
# Commit new files under data/ and push, rebasing on top of concurrent pushes from other workflows.
set -euo pipefail

msg="$1"
branch="${GITHUB_REF_NAME:?}"

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add data
if git diff --cached --quiet; then
  echo "No new data to commit"
  exit 0
fi
git commit -q -m "$msg"

for attempt in 1 2 3 4 5; do
  if git pull -q --rebase origin "$branch" && git push -q origin "HEAD:$branch"; then
    echo "Pushed on attempt $attempt"
    exit 0
  fi
  sleep $((attempt * 10))
done
echo "::error::push failed after 5 attempts"
exit 1
