"""EIA Open Data API v2 - hourly Form EIA-930 grid data for US balancing authorities.

Free key: https://www.eia.gov/opendata/register.php  ->  secret EIA_API_KEY
Tables (value in MWh; descriptive name columns are dropped to keep history compact - see README):
  energy/eia/region    : type D (demand), DF (day-ahead demand forecast), NG (net generation), TI (interchange)
  energy/eia/fuel_type : net generation by fueltype (SUN, WND, NG, COL, NUC, WAT, OIL, OTH, ...)
History: EIA-930 starts 2015-07-01; backfilled month by month.
"""
from datetime import date, datetime, timedelta, timezone
import time

import pandas as pd

from utils import backfill
from utils.http import check, env_int, require_env, session
from utils.storage import upsert

BASE = "https://api.eia.gov/v2/electricity/rto"
RESPONDENTS = ["CISO", "ERCO", "NYIS", "PJM", "MISO", "ISNE", "SWPP", "BPAT"]
PAGE = 5000
EARLIEST = date(2015, 7, 1)
ROUTES = [
    ("region-data", "energy/eia/region", "type"),
    ("fuel-type-data", "energy/eia/fuel_type", "fueltype"),
]


def fetch_route(http, api_key, route, start, end):
    rows, offset = [], 0
    while True:
        params = [
            ("api_key", api_key), ("frequency", "hourly"), ("data[0]", "value"),
            ("start", start), ("end", end),
            ("sort[0][column]", "period"), ("sort[0][direction]", "asc"),
            ("offset", offset), ("length", PAGE),
        ] + [("facets[respondent][]", r) for r in RESPONDENTS]
        r = check(http.get(f"{BASE}/{route}/data/", params=params, timeout=90))
        resp = r.json()["response"]
        batch = resp.get("data", [])
        rows.extend(batch)
        offset += len(batch)
        if not batch or offset >= int(resp.get("total", 0)):
            break
        time.sleep(1)
    return pd.DataFrame(rows)


def slim(df, key):
    if df.empty:
        return df
    out = df[["period", "respondent", key, "value"]].copy()
    out["period"] = pd.to_datetime(out["period"], utc=True).dt.strftime("%Y-%m-%dT%H:%MZ")
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    return out


def collect(http, api_key, start, end):
    """start/end: EIA hour strings 'YYYY-MM-DDTHH' (UTC, inclusive)."""
    got = 0
    for route, table, key in ROUTES:
        df = slim(fetch_route(http, api_key, route, start, end), key)
        got += len(df)
        upsert(df, table, ["period", "respondent", key], "period")
    return got


def main():
    backfill.register("energy", "eia", EARLIEST, EARLIEST)
    api_key = require_env("EIA_API_KEY")
    http = session()
    # EIA-930 values get revised for several days, so re-pull a rolling window and upsert.
    now = datetime.now(timezone.utc)
    start = (now - timedelta(days=env_int("EIA_LOOKBACK_DAYS", 7))).strftime("%Y-%m-%dT%H")
    collect(http, api_key, start, now.strftime("%Y-%m-%dT%H"))

    def fetch_month(first, last):
        if not collect(http, api_key, f"{first.isoformat()}T00", f"{last.isoformat()}T23"):
            raise backfill.Skip("no rows")

    backfill.run("energy", "eia", EARLIEST, EARLIEST, backfill.month_chunks, fetch_month)


if __name__ == "__main__":
    main()
