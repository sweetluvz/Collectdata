"""NYISO zonal Locational Based Marginal Prices - keyless public CSVs.

  energy/nyiso/lbmp_da : day-ahead hourly LBMP ($/MWh), timestamp (UTC) + one column per load zone
  energy/nyiso/lbmp_rt : real-time LBMP ($/MWh) as published in the zonal files - hourly, same layout
NYISO timestamps are Eastern prevailing time (interval start) and are converted to UTC; the repeated hour
when daylight saving ends is resolved from the order of the rows. Recent days come from daily CSVs,
history from monthly zip archives.
"""
from datetime import date, datetime, timedelta, timezone
import io
import time
import zipfile

import pandas as pd

from utils import backfill
from utils.http import check, session
from utils.storage import upsert

BASE = "http://mis.nyiso.com/public/csv"
MARKETS = {"da": "damlbmp", "rt": "rtlbmp"}
EARLIEST = date(2000, 1, 1)
RT_DEFAULT_START = EARLIEST
PRICE_COL = "LBMP ($/MWHr)"


def to_utc(local):
    ts = pd.to_datetime(local, format="%m/%d/%Y %H:%M")
    try:
        out = ts.dt.tz_localize("America/New_York", ambiguous="infer", nonexistent="shift_forward")
    except Exception:
        out = ts.dt.tz_localize("America/New_York", ambiguous="NaT", nonexistent="shift_forward")
    return out.dt.tz_convert("UTC")


def to_wide(csv_frames):
    if not csv_frames:
        return pd.DataFrame()
    df = pd.concat(csv_frames, ignore_index=True)
    parts = []
    for zone, g in df.groupby("Name", sort=False):
        utc = to_utc(g["Time Stamp"])
        parts.append(pd.Series(g[PRICE_COL].to_numpy(), index=utc, name=zone.strip()))
    wide = pd.concat([p[p.index.notna() & ~p.index.duplicated(keep="last")] for p in parts], axis=1)
    wide = wide.reindex(sorted(wide.columns), axis=1).sort_index()
    wide.index = wide.index.strftime("%Y-%m-%dT%H:%MZ")
    wide.index.name = "timestamp"
    return wide.reset_index()


def daily(http, market, day):
    r = http.get(f"{BASE}/{MARKETS[market]}/{day:%Y%m%d}{MARKETS[market]}_zone.csv", timeout=90)
    if r.status_code == 404:
        return []
    return [pd.read_csv(io.StringIO(check(r).text))]


def monthly(http, market, month_start):
    r = http.get(f"{BASE}/{MARKETS[market]}/{month_start:%Y%m}01{MARKETS[market]}_zone_csv.zip", timeout=180)
    if r.status_code == 404:
        return []
    with zipfile.ZipFile(io.BytesIO(check(r).content)) as z:
        return [pd.read_csv(z.open(n)) for n in sorted(z.namelist()) if n.endswith(".csv")]


def save(market, df):
    upsert(df, f"energy/nyiso/lbmp_{market}", ["timestamp"], "timestamp", cellwise=True)


def main():
    http = session()
    today = datetime.now(timezone.utc).date()
    for market in MARKETS:
        frames = []
        for d in range(-3, 2):  # day-ahead prices for tomorrow are published in the afternoon
            frames += daily(http, market, today + timedelta(days=d))
            time.sleep(0.5)
        save(market, to_wide(frames))

    for market, default_start in (("da", EARLIEST), ("rt", RT_DEFAULT_START)):
        def fetch(first, last, market=market):
            frames = monthly(http, market, first.replace(day=1))
            time.sleep(1)
            if not frames:
                raise backfill.Skip("no archive for this month")
            save(market, to_wide(frames))

        backfill.run("energy", f"nyiso_{market}", default_start, EARLIEST, backfill.month_chunks, fetch)


if __name__ == "__main__":
    main()
