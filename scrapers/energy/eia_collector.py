"""EIA Open Data API v2 - hourly Form EIA-930 grid data for US balancing authorities.

Free key: https://www.eia.gov/opendata/register.php  ->  secret EIA_API_KEY
Tables:
  energy/eia/region    : demand (D), day-ahead demand forecast (DF), net generation (NG), total interchange (TI)
  energy/eia/fuel_type : net generation by fuel (SUN, WND, NG, COL, NUC, WAT, OIL, OTH, ...)
"""
from datetime import datetime, timedelta, timezone
import time

import pandas as pd

from utils.http import check, env_int, require_env, session
from utils.storage import upsert

BASE = "https://api.eia.gov/v2/electricity/rto"
RESPONDENTS = ["CISO", "ERCO", "NYIS", "PJM", "MISO", "ISNE", "SWPP", "BPAT"]
PAGE = 5000


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
    df = pd.DataFrame(rows)
    if not df.empty:
        df["period"] = pd.to_datetime(df["period"], utc=True).dt.strftime("%Y-%m-%dT%H:%MZ")
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df


def main():
    api_key = require_env("EIA_API_KEY")
    http = session()
    # EIA-930 values get revised for several days, so re-pull a rolling window and upsert.
    now = datetime.now(timezone.utc)
    start = (now - timedelta(days=env_int("EIA_LOOKBACK_DAYS", 7))).strftime("%Y-%m-%dT%H")
    end = now.strftime("%Y-%m-%dT%H")

    region = fetch_route(http, api_key, "region-data", start, end)
    upsert(region, "energy/eia/region", ["period", "respondent", "type"], "period")

    fuel = fetch_route(http, api_key, "fuel-type-data", start, end)
    upsert(fuel, "energy/eia/fuel_type", ["period", "respondent", "fueltype"], "period")


if __name__ == "__main__":
    main()
