import io
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
# mtime=0 makes gzip output byte-identical for identical data, so unchanged files never create new git blobs.
GZIP = {"method": "gzip", "mtime": 0}


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


def _as_text(df):
    return df.astype(object).where(df.notna(), "").astype(str)


def upsert(df, table, keys, time_col, ext=".csv"):
    """Merge rows into monthly partitions data/<table>/YYYY-MM<ext>.

    Rows sharing `keys` are replaced by the newest version, so re-collecting an overlapping
    window updates revised values instead of duplicating them. Files are rewritten only when
    their content actually changes.
    """
    if df is None or df.empty:
        print(f"[{table}] nothing to save")
        return 0

    out_dir = table_dir(table)
    month = pd.to_datetime(df[time_col], utc=True, errors="coerce", format="mixed")
    month = month.dt.strftime("%Y-%m").fillna("unknown")

    added = 0
    for m, part in df.groupby(month):
        path = out_dir / f"{m}{ext}"
        old = pd.read_csv(path, dtype=str, keep_default_na=False) if path.exists() else None
        merged = pd.concat([old, _as_text(part)], ignore_index=True) if old is not None else _as_text(part)
        merged = (
            merged.fillna("")
            .drop_duplicates(subset=keys, keep="last")
            .sort_values([time_col, *keys], kind="stable")
        )
        before = 0 if old is None else len(old)
        changed = write_if_changed(merged, path)
        added += len(merged) - before
        status = "updated" if changed else "unchanged"
        print(f"[{table}] {path.relative_to(DATA_DIR)}: {len(merged)} rows (+{len(merged) - before}, {status})")
    return added


def load_all(table, ext=".csv"):
    files = sorted((DATA_DIR / table).glob(f"*{ext}"))
    if not files:
        return pd.DataFrame()
    return pd.concat([pd.read_csv(f, dtype=str, keep_default_na=False) for f in files], ignore_index=True)
