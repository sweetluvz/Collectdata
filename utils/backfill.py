"""Resumable historical backfill.

A plan per source lives in data/<domain>/_backfill.json:
    {"<source>": {"start": "...", "end": "...", "total": N, "done": [...], "skipped": [...]}}
A source without a plan gets its default history plan on its first run; BACKFILL_START creates or widens
a plan explicitly. Every later run - scheduled or manual - continues the remaining chunks until the time
budget runs out, so a multi-year backfill completes across
several runs without supervision. Progress is committed together with the data.
"""
from datetime import date, timedelta
import json
import os
import time

import requests

from utils.http import env_int
from utils import storage

PERMANENT_HTTP = (400, 404, 422)
# Sources that can have a backfill plan; plans of any other (removed) source are pruned by the catalog build.
SOURCES = {
    "energy": {"era5", "airquality", "eia", "eia_bulk", "eia_market", "europe_power", "europe_price", "gb", "aemo",
               "nyiso_da", "nyiso_rt"},
}
_deadline = None


def deadline():
    """One time budget per process, shared by every source the collector backfills."""
    global _deadline
    if _deadline is None:
        _deadline = time.monotonic() + env_int("BACKFILL_MINUTES", 90) * 60
    return _deadline


class Skip(Exception):
    """Chunk has no data at the source (or is outside its coverage) - record it and move on."""


def state_path(domain):
    return storage.DATA_DIR / domain / "_backfill.json"


def load_state(domain):
    p = state_path(domain)
    return json.loads(p.read_text()) if p.exists() else {}


def save_state(domain, state):
    p = state_path(domain)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, indent=1, sort_keys=True) + "\n")


def prune(domain):
    state = load_state(domain)
    stale = set(state) - SOURCES.get(domain, set())
    if stale:
        save_state(domain, {k: v for k, v in state.items() if k not in stale})
    return stale


def requested(source):
    """Return (start, end) if this run asks to (re)plan `source`, else None."""
    raw = os.environ.get("BACKFILL_START", "").strip()
    wanted = [s.strip() for s in os.environ.get("BACKFILL_SOURCES", "").split(",") if s.strip()]
    if not raw or (wanted and source not in wanted):
        return None
    end_raw = os.environ.get("BACKFILL_END", "").strip()
    start = None if raw == "auto" else date.fromisoformat(raw)
    end = date.fromisoformat(end_raw) if end_raw else date.today()
    return start, end


def month_chunks(start, end):
    """[(chunk_id, first_day, last_day)] covering start..end by calendar month."""
    out, cur = [], date(start.year, start.month, 1)
    while cur <= end:
        nxt = date(cur.year + (cur.month == 12), cur.month % 12 + 1, 1)
        out.append((cur.strftime("%Y-%m"), max(cur, start), min(nxt - timedelta(days=1), end)))
        cur = nxt
    return out


def year_chunks(start, end):
    return [
        (str(y), max(date(y, 1, 1), start), min(date(y, 12, 31), end))
        for y in range(start.year, end.year + 1)
    ]


def flag_incomplete(source):
    flag = os.environ.get("BACKFILL_FLAG")
    if flag:
        with open(flag, "a") as f:
            f.write(source + "\n")


def register(domain, source, default_start, earliest):
    """Create or widen the plan when this run requests a backfill. Safe to call before API keys are
    checked, so a plan made today is carried out by the first run that has the key."""
    req = requested(source)
    state = load_state(domain)
    if not req:
        # Sources get their default history automatically (BACKFILL_AUTO=0 disables this); an existing plan is
        # only widened when the default start moved earlier, so a manual dispatch that gets cancelled (a
        # pending run is replaced by the next one) cannot lose a widened history.
        if os.environ.get("BACKFILL_AUTO", "1") == "0":
            return
        if source in state and state[source]["start"] <= max(default_start, earliest).isoformat():
            return
        req = (None, date.fromisoformat(state[source]["end"]) if source in state else date.today())
    start, end = req
    start = max(start or default_start, earliest)
    old = state.get(source, {})
    state[source] = {
        "start": min(start.isoformat(), old.get("start", "9999")),
        "end": max(end.isoformat(), old.get("end", "")),
        "done": old.get("done", []),
        "skipped": old.get("skipped", []),
        "total": old.get("total", 0),
    }
    save_state(domain, state)


def run(domain, source, default_start, earliest, chunker, fetch):
    """Plan (if requested) and continue the backfill of one source.

    chunker(start, end) -> [(chunk_id, first, last, *extra)]; fetch(first, last, *extra) saves one chunk.
    """
    register(domain, source, default_start, earliest)
    state = load_state(domain)
    plan = state.get(source)
    if not plan:
        return
    chunks = chunker(date.fromisoformat(plan["start"]), date.fromisoformat(plan["end"]))
    plan["total"] = len(chunks)
    finished = set(plan["done"]) | set(plan["skipped"])
    todo = [c for c in chunks if c[0] not in finished]
    save_state(domain, state)
    if not todo:
        return

    end_at = deadline()
    left = int((end_at - time.monotonic()) // 60)
    print(f"[backfill:{source}] {len(todo)}/{len(chunks)} chunks remaining, {left} min left in this run")
    durations = []
    for chunk_id, *args in todo:
        remaining = end_at - time.monotonic()
        # Stop before a chunk that would likely overrun the budget (and the step timeout behind it).
        if remaining <= 0 or (durations and sum(durations) / len(durations) > remaining):
            print(f"::notice::backfill {source}: time budget used, {len(todo)} chunks left for the next run")
            flag_incomplete(source)
            return
        started = time.monotonic()
        try:
            fetch(*args)
            plan["done"].append(chunk_id)
        except Skip as e:
            print(f"[backfill:{source}] {chunk_id}: skipped ({e})")
            plan["skipped"].append(chunk_id)
        except requests.HTTPError as e:
            status = getattr(e.response, "status_code", None)
            if status in PERMANENT_HTTP:
                print(f"::warning::backfill {source} {chunk_id}: {e} - skipped")
                plan["skipped"].append(chunk_id)
            else:
                print(f"::warning::backfill {source} {chunk_id}: {e} - will retry next run")
                flag_incomplete(source)  # keep the self-dispatch chain going (bounded by MAX_CHAIN)
                return
        except Exception as e:
            print(f"::warning::backfill {source} {chunk_id}: {type(e).__name__}: {e} - will retry next run")
            flag_incomplete(source)
            return
        finally:
            durations.append(time.monotonic() - started)
            plan["done"].sort()
            plan["skipped"].sort()
            save_state(domain, state)
        todo = todo[1:]
    print(f"[backfill:{source}] complete ({plan['start']} .. {plan['end']})")
