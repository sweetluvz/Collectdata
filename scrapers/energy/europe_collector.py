"""European power system via Energy-Charts (Fraunhofer ISE) - keyless, CC BY 4.0.

Replaces ENTSO-E (which needs an approved token). Tables:
  energy/europe/power : timestamp (UTC), country, one column per production type as published
                        (e.g. "Solar", "Wind onshore", "Fossil gas", "Load", "Residual load",
                        "Cross border electricity trading"); MW, mostly 15-minute resolution
  energy/europe/price : timestamp (UTC), one column per bidding zone; day-ahead price in EUR/MWh
History is backfilled per (month, country) from 2015.
"""
from datetime import date, datetime, timedelta, timezone
import time

import pandas as pd
import requests

from utils import backfill
from utils.http import check, session
from utils.storage import upsert

BASE = "https://api.energy-charts.info"
COUNTRIES = ["de", "fr", "es", "it", "nl", "be", "at", "pl", "ch", "dk"]
BIDDING_ZONES = ["DE-LU", "FR", "ES", "NL", "BE", "AT", "PL", "CH", "DK1", "DK2", "NO2", "SE3", "IT-North"]
EARLIEST = date(2015, 1, 1)
PAUSE = 1.5


def iso(unix_seconds):
    return pd.to_datetime(pd.Series(unix_seconds), unit="s", utc=True).dt.strftime("%Y-%m-%dT%H:%MZ")


def fetch_power(http, country, first, last):
    r = check(http.get(f"{BASE}/public_power", params={
        "country": country, "start": first.isoformat(), "end": last.isoformat()}, timeout=120))
    js = r.json()
    ts = js.get("unix_seconds") or []
    if not ts:
        return pd.DataFrame()
    df = pd.DataFrame({"timestamp": iso(ts), "country": country.upper()})
    for p in js.get("production_types") or []:
        values = p.get("data") or []
        if len(values) == len(ts):
            df[p["name"]] = values
    return df.dropna(how="all", subset=[c for c in df.columns if c not in ("timestamp", "country")])


def fetch_prices(http, first, last):
    frames = []
    for zone in BIDDING_ZONES:
        try:
            r = check(http.get(f"{BASE}/price", params={
                "bzn": zone, "start": first.isoformat(), "end": last.isoformat()}, timeout=120))
            js = r.json()
            ts, price = js.get("unix_seconds") or [], js.get("price") or []
            if ts and len(ts) == len(price):
                frames.append(pd.DataFrame({"timestamp": iso(ts), zone: price}).set_index("timestamp"))
        except requests.RequestException as e:
            print(f"::warning::energy-charts price {zone} {first}..{last}: {e}")
        time.sleep(PAUSE)
    if not frames:
        return pd.DataFrame()
    wide = pd.concat(frames, axis=1)
    wide = wide[~wide.index.duplicated(keep="last")]
    return wide.dropna(how="all").reset_index()


def save_power(df):
    upsert(df, "energy/europe/power", ["timestamp", "country"], "timestamp", cellwise=True)


def save_prices(df):
    upsert(df, "energy/europe/price", ["timestamp"], "timestamp", cellwise=True)


def main():
    http = session()
    today = datetime.now(timezone.utc).date()
    first, last = today - timedelta(days=3), today + timedelta(days=1)
    failures = 0
    for country in COUNTRIES:
        try:
            save_power(fetch_power(http, country, first, last))
        except requests.RequestException as e:
            failures += 1
            print(f"::warning::energy-charts power {country}: {e}")
        time.sleep(PAUSE)
    save_prices(fetch_prices(http, first, last))
    if failures == len(COUNTRIES):
        raise SystemExit("energy-charts: every country failed")

    def fetch_country_month(first, last, country):
        df = fetch_power(http, country, first, last)
        time.sleep(PAUSE)
        if df.empty:
            raise backfill.Skip("no data")
        save_power(df)

    def fetch_price_month(first, last):
        df = fetch_prices(http, first, last)
        if df.empty:
            raise backfill.Skip("no prices")
        save_prices(df)

    # Prices are one small request set per month; run them first so the long power backfill cannot starve them.
    backfill.run("energy", "europe_price", EARLIEST, EARLIEST, backfill.month_chunks, fetch_price_month)
    backfill.run(
        "energy", "europe_power", EARLIEST, EARLIEST,
        lambda s, e: [(f"{cid}/{c}", f, l, c) for cid, f, l in backfill.month_chunks(s, e) for c in COUNTRIES],
        fetch_country_month,
    )


if __name__ == "__main__":
    main()
