#!/usr/bin/env bash
# Usage: continue_backfill.sh <workflow file>
# If a collector stopped because its time budget ran out (it writes its name to $BACKFILL_FLAG),
# dispatch the same workflow again. The plan is stored in data/<domain>/_backfill.json, so the new run
# needs no inputs. CHAIN caps consecutive self-dispatches; scheduled runs keep going after the cap.
set -euo pipefail

workflow="$1"
chain="${CHAIN:-0}"
max_chain="${MAX_CHAIN:-40}"

if [ ! -s "${BACKFILL_FLAG:?}" ]; then
  echo "No unfinished backfill"
  exit 0
fi
echo "Unfinished backfill: $(sort -u "$BACKFILL_FLAG" | tr '\n' ' ')"
if [ "$chain" -ge "$max_chain" ]; then
  echo "::warning::chain limit $max_chain reached - scheduled runs will continue the backfill"
  exit 0
fi
gh workflow run "$workflow" --repo "$GITHUB_REPOSITORY" --ref "$GITHUB_REF_NAME" -f chain="$((chain + 1))"
echo "Dispatched $workflow (chain $((chain + 1)))"
