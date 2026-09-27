"""ENTSO-E Transparency Platform via entsoe-py.

Token: register at https://transparency.entsoe.eu, then email transparency@entsoe.eu asking for
"Restful API access"  ->  secret ENTSOE_API_KEY.
GB is not included: it stopped publishing to ENTSO-E after Brexit.
One table per dataset (energy/entsoe/<dataset>), wide format: timestamp, country, <one column per series>.
History: the platform starts in 2015; backfilled per (year, zone, dataset).
"""
from datetime import date, datetime, timedelta, timezone
import time

import pandas as pd
from entsoe import EntsoePandasClient
from entsoe.exceptions import NoMatchingDataError

from utils import backfill
from utils.http import env_int, require_env
from utils.storage import upsert

ZONES = ["DE_LU", "FR", "ES", "NL", "BE", "PL", "AT"]
EARLIEST = date(2015, 1, 1)

QUERIES = {
    "load": lambda c, z, s, e: c.query_load(z, start=s, end=e),
    "load_forecast": lambda c, z, s, e: c.query_load_forecast(z, start=s, end=e),
    "generation": lambda c, z, s, e: c.query_generation(z, start=s, end=e, psr_type=None),
    "wind_solar_forecast": lambda c, z, s, e: c.query_wind_and_solar_forecast(z, start=s, end=e, psr_type=None),
    "day_ahead_price": lambda c, z, s, e: c.query_day_ahead_prices(z, start=s, end=e),
}


def to_wide(obj, zone, dataset):
    df = obj.to_frame(name=dataset) if isinstance(obj, pd.Series) else obj.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [" | ".join(str(x) for x in col if str(x)) for col in df.columns]
    df.index = pd.to_datetime(df.index, utc=True).strftime("%Y-%m-%dT%H:%MZ")
    df.index.name = "timestamp"
    df = df.dropna(how="all").reset_index()
    df.insert(1, "country", zone)
    return df


def save(df, dataset):
    upsert(df, f"energy/entsoe/{dataset}", ["timestamp", "country"], "timestamp")


def main():
    backfill.register("energy", "entsoe", EARLIEST, EARLIEST)
    client = EntsoePandasClient(api_key=require_env("ENTSOE_API_KEY"))
    now = pd.Timestamp(datetime.now(timezone.utc)).floor("h")
    start = now - timedelta(days=env_int("ENTSOE_LOOKBACK_DAYS", 3))
    end = now + timedelta(days=1)  # includes day-ahead prices / forecasts published for tomorrow

    failures, total = 0, 0
    for name, query in QUERIES.items():
        frames = []
        for zone in ZONES:
            total += 1
            try:
                frames.append(to_wide(query(client, zone, start, end), zone, name))
            except Exception as e:
                failures += 1
                print(f"::warning::entsoe {zone}/{name}: {type(e).__name__}: {e}")
            time.sleep(1)
        if frames:
            save(pd.concat(frames, ignore_index=True), name)
    if failures == total:
        raise SystemExit("entsoe: every query failed")

    def fetch(first, last, zone, name):
        s = pd.Timestamp(first, tz="UTC")
        e = pd.Timestamp(last + timedelta(days=1), tz="UTC")
        try:
            df = to_wide(QUERIES[name](client, zone, s, e), zone, name)
        except NoMatchingDataError:
            raise backfill.Skip("no matching data")
        save(df, name)
        time.sleep(1)

    backfill.run(
        "energy", "entsoe", EARLIEST, EARLIEST,
        lambda s, e: [
            (f"{cid}/{zone}/{name}", first, last, zone, name)
            for cid, first, last in backfill.year_chunks(s, e)
            for zone in ZONES
            for name in QUERIES
        ],
        fetch,
    )


if __name__ == "__main__":
    main()
