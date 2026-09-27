from datetime import date
import io
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
# mtime=0 makes gzip output byte-identical for identical data, so unchanged files never create new git blobs.
GZIP = {"method": "gzip", "mtime": 0}
# Months older than this stay frozen, so they are stored gzipped; recent months stay plain CSV because
# git delta-compresses the small appends made every run.
HOT_MONTHS = 2


def table_dir(table):
    path = DATA_DIR / table
    path.mkdir(parents=True, exist_ok=True)
    return path


def to_bytes(df, gz):
    buf = io.BytesIO()
    df.to_csv(buf, index=False, compression=GZIP if gz else None)
    return buf.getvalue()


def write_if_changed(df, path):
    data = to_bytes(df, path.suffix == ".gz")
    if path.exists() and path.read_bytes() == data:
        return False
    path.write_bytes(data)
    return True


def is_cold(month, today=None):
    if month == "unknown":
        return False
    today = today or date.today()
    y, m = map(int, month.split("-"))
    return (today.year - y) * 12 + (today.month - m) > HOT_MONTHS


def data_files(directory):
    return sorted([*directory.glob("*.csv"), *directory.glob("*.csv.gz")])


def _as_text(df):
    return df.astype(object).where(df.notna(), "").astype(str)


def _read(path):
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def upsert(df, table, keys, time_col, gzip=None):
    """Merge rows into monthly partitions data/<table>/YYYY-MM.csv[.gz].

    Rows sharing `keys` are replaced by the newest version, so re-collecting an overlapping window
    updates revised values instead of duplicating them. gzip=None stores cold months gzipped and hot
    months as plain CSV; files are rewritten only when their content changes.
    """
    if df is None or df.empty:
        print(f"[{table}] nothing to save")
        return 0

    out_dir = table_dir(table)
    month = pd.to_datetime(df[time_col], utc=True, errors="coerce", format="mixed")
    month = month.dt.strftime("%Y-%m").fillna("unknown")

    added = 0
    for m, part in df.groupby(month):
        use_gz = is_cold(m) if gzip is None else gzip
        path = out_dir / f"{m}.csv{'.gz' if use_gz else ''}"
        sibling = out_dir / f"{m}.csv{'' if use_gz else '.gz'}"
        olds = [_read(p) for p in (sibling, path) if p.exists()]
        before = sum(len(o) for o in olds)
        merged = pd.concat([*olds, _as_text(part)], ignore_index=True)
        merged = (
            merged.fillna("")
            .drop_duplicates(subset=keys, keep="last")
            .sort_values([time_col, *keys], kind="stable")
        )
        changed = write_if_changed(merged, path)
        if sibling.exists():
            sibling.unlink()
            changed = True
        added += len(merged) - before
        status = "updated" if changed else "unchanged"
        print(f"[{table}] {path.relative_to(DATA_DIR)}: {len(merged)} rows (+{len(merged) - before}, {status})")
    return added


def compact(domain):
    """Gzip plain-CSV monthly partitions that have gone cold. Returns the number of files converted."""
    converted = 0
    for path in (DATA_DIR / domain).rglob("*.csv"):
        month = path.name[:-4]
        if len(month) == 7 and month[4] == "-" and is_cold(month):
            write_if_changed(_read(path), path.with_suffix(".csv.gz"))
            path.unlink()
            converted += 1
    return converted


def load_all(table):
    files = data_files(DATA_DIR / table)
    if not files:
        return pd.DataFrame()
    return pd.concat([_read(f) for f in files], ignore_index=True)
