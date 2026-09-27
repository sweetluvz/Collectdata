"""Zillow Research public datasets (ZHVI home values, ZORI rents).

Scraping zillow.com listings violates Zillow's Terms of Use and is blocked by bot protection, so this
collector uses the free research CSVs instead. Every monthly release already contains the full history
(from 2000 for ZHVI, 2015 for ZORI), so only the newest release is kept as
realestate/zillow/<dataset>/<latest-month>.csv.gz (wide: one row per region, one column per month).
Earlier releases remain available in git history.
"""
import io
import re

import pandas as pd

from utils.http import check, session
from utils.storage import table_dir, write_if_changed

BASE = "https://files.zillowstatic.com/research/public_csvs"
DATASETS = {
    "zhvi_metro": f"{BASE}/zhvi/Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
    "zhvi_county": f"{BASE}/zhvi/County_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
    "zori_metro": f"{BASE}/zori/Metro_zori_uc_sfrcondomfr_sm_month.csv",
}


def main():
    http = session()
    failures = 0
    for name, url in DATASETS.items():
        try:
            df = pd.read_csv(io.BytesIO(check(http.get(url, timeout=120)).content))
        except Exception as e:
            failures += 1
            print(f"::warning::zillow {name}: {e}")
            continue
        months = sorted(c for c in df.columns if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(c)))
        latest = months[-1][:7] if months else "unknown"
        out_dir = table_dir(f"realestate/zillow/{name}")
        path = out_dir / f"{latest}.csv.gz"
        if path.exists():
            print(f"[zillow] {name}: release {latest} already stored")
            continue
        write_if_changed(df, path)
        for old in out_dir.glob("*.csv.gz"):
            if old != path:
                old.unlink()
        print(f"[zillow] {name}: saved release {latest} ({len(df)} regions x {len(months)} months)")
    if failures == len(DATASETS):
        raise SystemExit("zillow: every dataset failed")


if __name__ == "__main__":
    main()
