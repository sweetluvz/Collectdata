"""EIA Open Data API v2 (free key: https://www.eia.gov/opendata/register.php -> secret EIA_API_KEY).

Hourly Form EIA-930 grid data for ALL balancing authorities, stored wide (one row per hour, one column per
series) so the full 2015+ history stays small:
  energy/eia/region      : <BA>_<type>  type D demand, DF day-ahead demand forecast, NG net generation, TI interchange
  energy/eia/fuel_type   : <BA>_<fuel>  net generation by fuel (SUN, WND, NG, COL, NUC, WAT, OIL, OTH, ...)
  energy/eia/interchange : <FROM>><TO>  hourly flow between neighbouring BAs (edges of the grid graph)
  energy/eia/subregion   : <BA>_<subregion>  demand of sub-BA zones (e.g. PJM zones, ERCOT weather zones)
Long-format market tables:
  energy/eia/fuel_prices  : daily spot/futures prices (WTI, Brent, Henry Hub, products; since 1986)
  energy/eia/retail_sales : monthly retail electricity price (cents/kWh), revenue (M$), sales (MWh),
                            customers by state and sector (since 2001)
History is backfilled month by month (EIA-930 starts 2015-07-01) and year by year (market tables).
"""
from datetime import date, datetime, timedelta, timezone
import time

import pandas as pd

from utils import backfill
from utils.http import check, env_int, require_env, session
from utils.storage import upsert

BASE = "https://api.eia.gov/v2"
PAGE = 5000
EARLIEST = date(2015, 7, 1)
MARKET_EARLIEST = date(1986, 1, 1)

# route, table, column-name builder
HOURLY = [
    ("electricity/rto/region-data", "energy/eia/region", lambda r: f"{r['respondent']}_{r['type']}"),
    ("electricity/rto/fuel-type-data", "energy/eia/fuel_type", lambda r: f"{r['respondent']}_{r['fueltype']}"),
    ("electricity/rto/interchange-data", "energy/eia/interchange", lambda r: f"{r['fromba']}>{r['toba']}"),
    ("electricity/rto/region-sub-ba-data", "energy/eia/subregion", lambda r: f"{r['parent']}_{r['subba']}"),
]
# route, frequency, data fields, table, keys, {source column: stored column}
MARKET = [
    ("natural-gas/pri/fut", "daily", ["value"], "energy/eia/fuel_prices", ["period", "series"],
     {"series-description": "description", "area-name": "area", "units": "units"}),
    ("petroleum/pri/spt", "daily", ["value"], "energy/eia/fuel_prices", ["period", "series"],
     {"series-description": "description", "area-name": "area", "units": "units"}),
    ("electricity/retail-sales", "monthly", ["price", "revenue", "sales", "customers"], "energy/eia/retail_sales",
     ["period", "stateid", "sectorid"], {}),
]


def fetch(http, api_key, route, frequency, start, end, fields=("value",)):
    rows, offset = [], 0
    while True:
        params = [
            ("api_key", api_key), ("frequency", frequency),
            *[(f"data[{i}]", f) for i, f in enumerate(fields)],
            ("start", start), ("end", end),
            ("sort[0][column]", "period"), ("sort[0][direction]", "asc"),
            ("offset", offset), ("length", PAGE),
        ]
        r = check(http.get(f"{BASE}/{route}/data/", params=params, timeout=120))
        resp = r.json()["response"]
        batch = resp.get("data", [])
        rows.extend(batch)
        offset += len(batch)
        if not batch or offset >= int(resp.get("total", 0)):
            break
        time.sleep(0.5)
    return rows


def to_wide(rows, column):
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["column"] = [column(r) for r in rows]
    df["period"] = pd.to_datetime(df["period"], utc=True).dt.strftime("%Y-%m-%dT%H:%MZ")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    wide = df.pivot_table(index="period", columns="column", values="value", aggfunc="last")
    wide = wide.reindex(sorted(wide.columns), axis=1)
    return wide.reset_index()


def collect_hourly(http, api_key, start, end):
    """start/end: EIA hour strings 'YYYY-MM-DDTHH' (UTC, inclusive). Returns rows saved."""
    got = 0
    for route, table, column in HOURLY:
        wide = to_wide(fetch(http, api_key, route, "hourly", start, end), column)
        got += len(wide)
        upsert(wide, table, ["period"], "period", cellwise=True)
    return got


def collect_market(http, api_key, start, end):
    """start/end: 'YYYY-MM-DD'. Monthly routes get 'YYYY-MM'."""
    got = 0
    for route, frequency, fields, table, keys, rename in MARKET:
        s, e = (start, end) if frequency == "daily" else (start[:7], end[:7])
        rows = fetch(http, api_key, route, frequency, s, e, fields)
        if not rows:
            continue
        df = pd.DataFrame(rows)
        df = df[[*keys, *[c for c in rename if c in df.columns], *fields]].rename(columns=rename)
        for f in fields:
            df[f] = pd.to_numeric(df[f], errors="coerce")
        got += len(df)
        upsert(df, table, keys, "period")
    return got


def main():
    backfill.register("energy", "eia", EARLIEST, EARLIEST)
    backfill.register("energy", "eia_market", MARKET_EARLIEST, MARKET_EARLIEST)
    api_key = require_env("EIA_API_KEY")
    http = session()
    # EIA-930 values get revised for several days, so re-pull a rolling window and upsert.
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=env_int("EIA_LOOKBACK_DAYS", 7))
    collect_hourly(http, api_key, start.strftime("%Y-%m-%dT%H"), now.strftime("%Y-%m-%dT%H"))
    collect_market(http, api_key, (now - timedelta(days=90)).strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d"))

    def fetch_month(first, last):
        if not collect_hourly(http, api_key, f"{first.isoformat()}T00", f"{last.isoformat()}T23"):
            raise backfill.Skip("no rows")

    def fetch_market_year(first, last):
        if not collect_market(http, api_key, first.isoformat(), last.isoformat()):
            raise backfill.Skip("no rows")

    backfill.run("energy", "eia", EARLIEST, EARLIEST, backfill.month_chunks, fetch_month)
    backfill.run("energy", "eia_market", MARKET_EARLIEST, MARKET_EARLIEST, backfill.year_chunks, fetch_market_year)


if __name__ == "__main__":
    main()
