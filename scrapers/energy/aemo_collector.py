"""AEMO National Electricity Market (Australia) - keyless monthly CSVs.

Table energy/aemo/price_demand (wide): timestamp (UTC), <REGION>_demand (MW), <REGION>_price (AUD/MWh)
for NSW1, QLD1, VIC1, SA1, TAS1. Interval is 30 min before Oct 2021 and 5 min after (5-minute settlement).
SETTLEMENTDATE is NEM time (UTC+10, no daylight saving) at the END of the interval; it is converted to UTC.
History: backfilled month by month from the start of the NEM (Dec 1998).
"""
from datetime import date, datetime, timedelta, timezone
import io
import time

import pandas as pd

from utils import backfill
from utils.http import check, session
from utils.storage import upsert

URL = "https://aemo.com.au/aemo/data/nem/priceanddemand/PRICE_AND_DEMAND_{ym}_{region}.csv"
REGIONS = ["NSW1", "QLD1", "VIC1", "SA1", "TAS1"]
EARLIEST = date(1998, 12, 1)
NEM_UTC_OFFSET = timedelta(hours=10)


def fetch_month(http, year, month):
    frames = []
    for region in REGIONS:
        r = http.get(URL.format(ym=f"{year}{month:02d}", region=region), timeout=90)
        if r.status_code == 404:
            continue
        df = pd.read_csv(io.StringIO(check(r).text))
        raw = df["SETTLEMENTDATE"].astype(str).str.strip()
        ts = pd.to_datetime(raw, format="%Y/%m/%d %H:%M:%S", errors="coerce").fillna(
            pd.to_datetime(raw, format="%Y/%m/%d %H:%M", errors="coerce"))  # pre-2021 files omit seconds
        ts = ts - NEM_UTC_OFFSET
        frames.append(pd.DataFrame({
            "timestamp": ts.dt.strftime("%Y-%m-%dT%H:%MZ"),
            f"{region}_demand": pd.to_numeric(df["TOTALDEMAND"], errors="coerce"),
            f"{region}_price": pd.to_numeric(df["RRP"], errors="coerce"),
        }).set_index("timestamp"))
        time.sleep(1)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, axis=1).reset_index()


def save(df):
    upsert(df, "energy/aemo/price_demand", ["timestamp"], "timestamp", cellwise=True)


def main():
    http = session()
    today = datetime.now(timezone.utc).date()
    prev = today.replace(day=1) - timedelta(days=1)
    for d in (prev, today):
        save(fetch_month(http, d.year, d.month))

    def fetch(first, last):
        df = fetch_month(http, first.year, first.month)
        if df.empty:
            raise backfill.Skip("no files for this month")
        save(df)

    backfill.run("energy", "aemo", EARLIEST, EARLIEST, backfill.month_chunks, fetch)


if __name__ == "__main__":
    main()
