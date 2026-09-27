"""Zillow Research public datasets (ZHVI home values, ZORI rents).

Scraping zillow.com listings violates Zillow's Terms of Use and is blocked by bot protection, so this
collector uses the free research CSVs instead. They are updated monthly; each new release is saved once
as a gzipped snapshot named after its latest month column.
"""
import io
import re

import pandas as pd

from utils.http import session
from utils.storage import DATA_DIR

BASE = "https://files.zillowstatic.com/research/public_csvs"
DATASETS = {
    "zhvi_metro": f"{BASE}/zhvi/Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
    "zhvi_county": f"{BASE}/zhvi/County_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
    "zhvi_city": f"{BASE}/zhvi/City_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
    "zori_metro": f"{BASE}/zori/Metro_zori_uc_sfrcondomfr_sm_month.csv",
}


def main():
    http = session()
    out_dir = DATA_DIR / "realestate" / "zillow"
    out_dir.mkdir(parents=True, exist_ok=True)
    failures = 0
    for name, url in DATASETS.items():
        try:
            r = http.get(url, timeout=120)
            r.raise_for_status()
            df = pd.read_csv(io.BytesIO(r.content))
        except Exception as e:
            failures += 1
            print(f"::warning::zillow {name}: {e}")
            continue
        months = sorted(c for c in df.columns if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(c)))
        latest = months[-1][:7] if months else "unknown"
        path = out_dir / f"{name}_{latest}.csv.gz"
        if path.exists():
            print(f"[zillow] {name}: release {latest} already stored")
            continue
        df.to_csv(path, index=False, compression="gzip")
        print(f"[zillow] {name}: saved release {latest} ({len(df)} regions x {len(months)} months)")
    if failures == len(DATASETS):
        raise SystemExit("zillow: every dataset failed")


if __name__ == "__main__":
    main()
