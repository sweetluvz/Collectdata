"""Write data/<domain>/CATALOG.md listing every table: files, rows, time coverage, size.

Output contains no generation timestamp, so it only changes when the data changes.
Usage: python scripts/build_catalog.py energy|realestate|patents
"""
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.storage import DATA_DIR  # noqa: E402

TIME_COLS = ["issued_at", "time", "period", "timestamp", "scraped_at", "fetched_at", "patent_date", "date_published"]


def data_files(d):
    return sorted([*d.glob("*.csv"), *d.glob("*.csv.gz")])


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def describe(table_dir):
    files = data_files(table_dir)
    size = sum(f.stat().st_size for f in files)
    header = pd.read_csv(files[0], nrows=0).columns
    time_col = next((c for c in TIME_COLS if c in header), None)
    if time_col is None:  # wide snapshot tables (Zillow): one file per release
        return len(files), "", files[0].name.split(".")[0], files[-1].name.split(".")[0], size, "release"
    col = pd.concat([pd.read_csv(f, usecols=[time_col], dtype=str, keep_default_na=False)[time_col] for f in files])
    col = col[col != ""]
    return len(files), len(col), col.min() if len(col) else "", col.max() if len(col) else "", size, time_col


def build(domain):
    root = DATA_DIR / domain
    tables = sorted({f.parent for f in root.rglob("*.csv*") if f.name.endswith((".csv", ".csv.gz"))})
    lines = [
        f"# Data catalog: `{domain}`",
        "",
        "Auto-generated after every collection run by `scripts/build_catalog.py`.",
        "",
        "| Table | Files | Rows | Time column | From | To | Size |",
        "|---|---:|---:|---|---|---|---:|",
    ]
    for t in tables:
        n_files, rows, first, last, size, time_col = describe(t)
        rel = t.relative_to(DATA_DIR).as_posix()
        rows_txt = f"{rows:,}" if rows != "" else "-"
        lines.append(f"| `{rel}` | {n_files} | {rows_txt} | `{time_col}` | {first} | {last} | {human(size)} |")
    if not tables:
        lines.append("| _(no data yet)_ | | | | | | |")
    root.mkdir(parents=True, exist_ok=True)
    (root / "CATALOG.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"catalog: {len(tables)} tables in {domain}")


if __name__ == "__main__":
    build(sys.argv[1])
