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
# A queued run of the same workflow will continue the stored plan anyway; dispatching another would
# replace it (GitHub keeps only one pending run per concurrency group) and could drop its inputs.
queued=$(gh run list --repo "$GITHUB_REPOSITORY" --workflow "$workflow" --limit 20 \
  --json status --jq '[.[] | select(.status == "queued" or .status == "pending" or .status == "waiting")] | length')
if [ "${queued:-0}" -gt 0 ]; then
  echo "A run of $workflow is already queued - it will continue the backfill"
  exit 0
fi
gh workflow run "$workflow" --repo "$GITHUB_REPOSITORY" --ref "$GITHUB_REF_NAME" -f chain="$((chain + 1))"
echo "Dispatched $workflow (chain $((chain + 1)))"
