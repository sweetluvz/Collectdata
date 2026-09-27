from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _as_text(df):
    return df.astype(object).where(df.notna(), "").astype(str)


def upsert(df, category, source, keys, time_col, prefix="", ext=".csv"):
    """Merge rows into monthly partitions data/<category>/<source>/<prefix>YYYY-MM<ext>.

    Rows with the same `keys` are replaced by the newest version, so re-collecting an
    overlapping window updates revised values instead of duplicating them.
    """
    if df is None or df.empty:
        print(f"[{source}] nothing to save")
        return 0

    out_dir = DATA_DIR / category / source
    out_dir.mkdir(parents=True, exist_ok=True)
    month = pd.to_datetime(df[time_col], utc=True, errors="coerce").dt.strftime("%Y-%m").fillna("unknown")

    added = 0
    for m, part in df.groupby(month):
        path = out_dir / f"{prefix}{m}{ext}"
        new = _as_text(part)
        if path.exists():
            old = pd.read_csv(path, dtype=str, keep_default_na=False)
            before = len(old)
            merged = pd.concat([old, new], ignore_index=True)
        else:
            before = 0
            merged = new
        merged = merged.drop_duplicates(subset=keys, keep="last").sort_values([time_col, *keys])
        merged.to_csv(path, index=False)
        added += len(merged) - before
        print(f"[{source}] {path.relative_to(DATA_DIR)}: {len(merged)} rows (+{len(merged) - before})")
    return added


def load_all(category, source, prefix="", ext=".csv"):
    out_dir = DATA_DIR / category / source
    files = sorted(out_dir.glob(f"{prefix}*{ext}"))
    if not files:
        return pd.DataFrame()
    return pd.concat([pd.read_csv(f, dtype=str, keep_default_na=False) for f in files], ignore_index=True)
