"""Free US housing research datasets (keyless). Every release already contains the full history, so only
the newest release of each dataset is kept as realestate/<source>/<dataset>/<latest-period>.csv.gz
(earlier releases stay in git history).

  zillow  : ZHVI home values (from 2000), ZORI rents (from 2015), for-sale inventory, sales count
            (Zillow Research; scraping zillow.com listings is not done - it violates Zillow's Terms of Use)
  fhfa    : FHFA House Price Index master file (all levels, from 1975)
  realtor : Realtor.com monthly inventory metrics by metro (from 2016)
"""
import io
import re

import pandas as pd

from utils.http import check, session
from utils.storage import table_dir, write_if_changed

ZILLOW = "https://files.zillowstatic.com/research/public_csvs"
DATASETS = {
    "zillow/zhvi_metro": f"{ZILLOW}/zhvi/Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
    "zillow/zhvi_county": f"{ZILLOW}/zhvi/County_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
    "zillow/zori_metro": f"{ZILLOW}/zori/Metro_zori_uc_sfrcondomfr_sm_month.csv",
    "zillow/inventory_metro": f"{ZILLOW}/invt_fs/Metro_invt_fs_uc_sfrcondo_sm_month.csv",
    "zillow/sales_count_metro": f"{ZILLOW}/sales_count_now/Metro_sales_count_now_uc_sfrcondo_month.csv",
    "fhfa/hpi_master": "https://www.fhfa.gov/hpi/download/monthly/hpi_master.csv",
    "realtor/inventory_metro": "https://econdata.s3-us-west-2.amazonaws.com/Reports/Core/RDC_Inventory_Core_Metrics_Metro_History.csv",
}


def latest_period(df):
    """Release label: newest period present in the file (YYYY-MM)."""
    dates = [c for c in df.columns if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(c))]
    if dates:
        return max(dates)[:7]
    if "month_date_yyyymm" in df.columns:
        v = str(pd.to_numeric(df["month_date_yyyymm"], errors="coerce").max())[:6]
        return f"{v[:4]}-{v[4:6]}"
    if {"yr", "period", "frequency"} <= set(df.columns):
        m = df[df["frequency"] == "monthly"]
        if not m.empty:
            y, p = max(zip(m["yr"].astype(int), m["period"].astype(int)))
            return f"{y}-{p:02d}"
    return "unknown"


def main():
    http = session()
    failures = 0
    for name, url in DATASETS.items():
        try:
            df = pd.read_csv(io.BytesIO(check(http.get(url, timeout=180)).content), low_memory=False)
        except Exception as e:
            failures += 1
            print(f"::warning::{name}: {e}")
            continue
        release = latest_period(df)
        out_dir = table_dir(f"realestate/{name}")
        path = out_dir / f"{release}.csv.gz"
        if path.exists():
            print(f"[{name}] release {release} already stored")
            continue
        write_if_changed(df, path)
        for old in out_dir.glob("*.csv.gz"):
            if old != path:
                old.unlink()
        print(f"[{name}] saved release {release} ({len(df):,} rows)")
    if failures == len(DATASETS):
        raise SystemExit("us housing: every dataset failed")


if __name__ == "__main__":
    main()
