"""Great Britain power system - keyless.

  energy/gb/generation       : Elexon BMRS FUELHH, half-hourly generation by fuel type (MW), wide; from 2016
  energy/gb/demand           : Elexon initial demand outturn INDO / ITSDO (MW), half-hourly
  energy/gb/carbon_intensity : NESO Carbon Intensity API, national gCO2/kWh forecast + actual; from 2017-09
All timestamps are the UTC start of the settlement period. Elexon allows at most 7 days per request,
the Carbon Intensity API 14 days, so each month is fetched in weekly windows.
"""
from datetime import date, datetime, timedelta, timezone
import time

import pandas as pd
import requests

from utils import backfill
from utils.http import check, session
from utils.storage import upsert

ELEXON = "https://data.elexon.co.uk/bmrs/api/v1"
CARBON = "https://api.carbonintensity.org.uk"
EARLIEST = date(2016, 1, 1)


def windows(first, last, days=7):
    cur = first
    while cur <= last:
        end = min(cur + timedelta(days=days - 1), last)
        yield cur, end
        cur = end + timedelta(days=1)


def utc(series):
    return pd.to_datetime(series, utc=True).dt.strftime("%Y-%m-%dT%H:%MZ")


def elexon(http, path, first, last):
    rows = []
    for a, b in windows(first, last):
        r = check(http.get(f"{ELEXON}/{path}", params={
            "settlementDateFrom": a.isoformat(), "settlementDateTo": b.isoformat(), "format": "json"}, timeout=120))
        rows.extend(r.json().get("data") or [])
        time.sleep(0.5)
    return pd.DataFrame(rows)


def generation(http, first, last):
    df = elexon(http, "datasets/FUELHH", first, last)
    if df.empty:
        return df
    df["startTime"] = utc(df["startTime"])
    wide = df.pivot_table(index="startTime", columns="fuelType", values="generation", aggfunc="last")
    return wide.reindex(sorted(wide.columns), axis=1).reset_index().rename(columns={"startTime": "timestamp"})


def demand(http, first, last):
    df = elexon(http, "demand/outturn", first, last)
    if df.empty:
        return df
    out = pd.DataFrame({
        "timestamp": utc(df["startTime"]),
        "indo": df.get("initialDemandOutturn"),
        "itsdo": df.get("initialTransmissionSystemDemandOutturn"),
    })
    return out.drop_duplicates("timestamp", keep="last")


def carbon(http, first, last):
    rows = []
    for a, b in windows(first, last, days=14):
        r = check(http.get(f"{CARBON}/intensity/{a.isoformat()}T00:00Z/{(b + timedelta(days=1)).isoformat()}T00:00Z",
                           timeout=120))
        for d in r.json().get("data") or []:
            i = d.get("intensity") or {}
            rows.append({"timestamp": d["from"], "forecast": i.get("forecast"), "actual": i.get("actual"),
                         "index": i.get("index")})
        time.sleep(0.5)
    df = pd.DataFrame(rows)
    if not df.empty:
        df["timestamp"] = utc(df["timestamp"])
    return df


def collect(http, first, last):
    got = 0
    for name, fn in (("generation", generation), ("demand", demand), ("carbon_intensity", carbon)):
        try:
            df = fn(http, first, last)
        except requests.HTTPError as e:
            if getattr(e.response, "status_code", 500) >= 500 or e.response.status_code == 429:
                raise
            print(f"::warning::gb {name} {first}..{last}: {e}")  # e.g. before the dataset starts
            continue
        got += len(df)
        upsert(df, f"energy/gb/{name}", ["timestamp"], "timestamp", cellwise=True)
    return got


def main():
    http = session()
    today = datetime.now(timezone.utc).date()
    collect(http, today - timedelta(days=6), today)

    def fetch_month(first, last):
        if not collect(http, first, last):
            raise backfill.Skip("no data")

    backfill.run("energy", "gb", EARLIEST, EARLIEST, backfill.month_chunks, fetch_month)


if __name__ == "__main__":
    main()
