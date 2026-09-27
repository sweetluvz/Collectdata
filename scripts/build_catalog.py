"""Compact cold partitions, then write data/<domain>/CATALOG.md: every table's files, rows, time coverage,
size, plus backfill progress.

Per-file stats are cached in data/<domain>/_catalog_cache.json keyed by content hash, so only changed files
are re-read. Output has no generation timestamp, so it only changes when the data changes.
Usage: python scripts/build_catalog.py energy|realestate|patents
"""
import hashlib
import json
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import storage  # noqa: E402
from utils.backfill import load_state  # noqa: E402

TIME_COLS = ["issued_at", "time", "period", "timestamp", "scraped_at", "fetched_at", "patent_date", "date_published"]


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def file_stats(path, cache):
    key = path.relative_to(storage.DATA_DIR).as_posix()
    digest = hashlib.sha1(path.read_bytes()).hexdigest()
    hit = cache.get(key)
    if hit and hit["sha1"] == digest:
        return hit
    header = pd.read_csv(path, nrows=0).columns
    time_col = next((c for c in TIME_COLS if c in header), None)
    if time_col is None:  # wide snapshot tables (Zillow): one file per release
        stats = {"rows": None, "min": "", "max": "", "time_col": "release"}
    else:
        col = pd.read_csv(path, usecols=[time_col], dtype=str, keep_default_na=False)[time_col]
        col = col[col != ""]
        stats = {"rows": len(col), "min": col.min() if len(col) else "", "max": col.max() if len(col) else "",
                 "time_col": time_col}
    cache[key] = {"sha1": digest, **stats}
    return cache[key]


def describe(table_dir, cache):
    files = storage.data_files(table_dir)
    stats = [file_stats(f, cache) for f in files]
    size = sum(f.stat().st_size for f in files)
    if stats[0]["time_col"] == "release":
        names = [f.name.split(".")[0] for f in files]
        return len(files), "-", "release", names[0], names[-1], size
    rows = sum(s["rows"] for s in stats)
    first = min((s["min"] for s in stats if s["min"]), default="")
    last = max((s["max"] for s in stats if s["max"]), default="")
    return len(files), f"{rows:,}", stats[0]["time_col"], first, last, size


def backfill_lines(domain):
    state = load_state(domain)
    if not state:
        return []
    lines = [
        "",
        "## Backfill progress",
        "",
        "| Source | Range | Chunks done | Skipped (no data) | Remaining |",
        "|---|---|---:|---:|---:|",
    ]
    for source, plan in sorted(state.items()):
        total = plan.get("total", 0)
        done, skipped = len(plan.get("done", [])), len(plan.get("skipped", []))
        remaining = max(total - done - skipped, 0)
        if not total:
            status = "waiting (API key missing?)"
        else:
            status = "complete" if not remaining else f"{remaining}"
        lines.append(f"| `{source}` | {plan['start']} .. {plan['end']} | {done} / {total} | {skipped} | {status} |")
    return lines


def build(domain):
    root = storage.DATA_DIR / domain
    root.mkdir(parents=True, exist_ok=True)
    converted = storage.compact(domain)
    if converted:
        print(f"compacted {converted} cold partitions to .csv.gz")

    cache_path = root / "_catalog_cache.json"
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    tables = sorted({f.parent for f in root.rglob("*") if f.name.endswith((".csv", ".csv.gz"))})
    lines = [
        f"# Data catalog: `{domain}`",
        "",
        "Auto-generated after every collection run by `scripts/build_catalog.py`.",
        "",
        "| Table | Files | Rows | Time column | From | To | Size |",
        "|---|---:|---:|---|---|---|---:|",
    ]
    for t in tables:
        n_files, rows, time_col, first, last, size = describe(t, cache)
        rel = t.relative_to(storage.DATA_DIR).as_posix()
        lines.append(f"| `{rel}` | {n_files} | {rows} | `{time_col}` | {first} | {last} | {human(size)} |")
    if not tables:
        lines.append("| _(no data yet)_ | | | | | | |")
    lines += backfill_lines(domain)

    live = {f.relative_to(storage.DATA_DIR).as_posix() for t in tables for f in storage.data_files(t)}
    cache = {k: v for k, v in sorted(cache.items()) if k in live}
    cache_path.write_text(json.dumps(cache, indent=1, sort_keys=True) + "\n")
    (root / "CATALOG.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"catalog: {len(tables)} tables in {domain}")


if __name__ == "__main__":
    build(sys.argv[1])
