"""ENTSO-E Transparency Platform via entsoe-py.

Token: register at https://transparency.entsoe.eu, then email transparency@entsoe.eu asking for
"Restful API access"  ->  secret ENTSOE_API_KEY.
GB is not included: it stopped publishing to ENTSO-E after Brexit.
One table per dataset (energy/entsoe/<dataset>), long format: timestamp, country, dataset, variable, value.
"""
from datetime import datetime, timedelta, timezone
import time

import pandas as pd
from entsoe import EntsoePandasClient

from utils.http import env_int, require_env
from utils.storage import upsert

ZONES = ["DE_LU", "FR", "ES", "NL", "BE", "PL", "AT"]

QUERIES = {
    "load": lambda c, z, s, e: c.query_load(z, start=s, end=e),
    "load_forecast": lambda c, z, s, e: c.query_load_forecast(z, start=s, end=e),
    "generation": lambda c, z, s, e: c.query_generation(z, start=s, end=e, psr_type=None),
    "wind_solar_forecast": lambda c, z, s, e: c.query_wind_and_solar_forecast(z, start=s, end=e, psr_type=None),
    "day_ahead_price": lambda c, z, s, e: c.query_day_ahead_prices(z, start=s, end=e),
}


def to_long(obj, zone, dataset):
    df = obj.to_frame(name=dataset) if isinstance(obj, pd.Series) else obj.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [" | ".join(str(x) for x in col if str(x)) for col in df.columns]
    df.index = pd.to_datetime(df.index, utc=True)
    df.index.name = "timestamp"
    out = df.reset_index().melt(id_vars="timestamp", var_name="variable", value_name="value")
    out = out.dropna(subset=["value"])
    out["timestamp"] = out["timestamp"].dt.strftime("%Y-%m-%dT%H:%MZ")
    out.insert(1, "country", zone)
    out.insert(2, "dataset", dataset)
    return out


def main():
    client = EntsoePandasClient(api_key=require_env("ENTSOE_API_KEY"))
    now = pd.Timestamp(datetime.now(timezone.utc)).floor("h")
    start = now - timedelta(days=env_int("ENTSOE_LOOKBACK_DAYS", 3))
    end = now + timedelta(days=1)  # includes day-ahead prices / forecasts published for tomorrow

    frames, failures, total = [], 0, 0
    for zone in ZONES:
        for name, query in QUERIES.items():
            total += 1
            try:
                frames.append(to_long(query(client, zone, start, end), zone, name))
            except Exception as e:
                failures += 1
                print(f"::warning::entsoe {zone}/{name}: {type(e).__name__}: {e}")
            time.sleep(1)

    if frames:
        df = pd.concat(frames, ignore_index=True)
        for dataset, part in df.groupby("dataset"):
            upsert(part, f"energy/entsoe/{dataset}", ["timestamp", "country", "variable"], "timestamp")
    if failures == total:
        raise SystemExit("entsoe: every query failed")


if __name__ == "__main__":
    main()
