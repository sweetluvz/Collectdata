"""Open-Meteo weather + air quality (no API key).

Tables:
  energy/weather/era5        : ERA5 reanalysis (Open-Meteo archive, ~5 day delay). Continuous history:
                               backfill fills the past, every run appends the latest days.
  energy/weather/observed    : latest value per (location, time) over the last days (forecast-model analysis)
  energy/weather/forecast    : every forecast issue kept separately (issued_at, time) - lets STLF models be
                               evaluated with the weather forecasts actually available at prediction time
  energy/airquality/observed : hourly pollutants + US AQI (CAMS)
"""
from datetime import date, datetime, timedelta, timezone
import time

import pandas as pd

from utils import backfill
from utils.http import check, env_int, session
from utils.storage import upsert

# Near load centres of EIA balancing authorities, GB, the Australian NEM regions, EU capitals and VN cities.
LOCATIONS = [
    ("US_CISO_LosAngeles", 34.05, -118.24),
    ("US_CISO_SanFrancisco", 37.77, -122.42),
    ("US_ERCO_Houston", 29.76, -95.37),
    ("US_ERCO_Dallas", 32.78, -96.80),
    ("US_NYIS_NewYork", 40.71, -74.01),
    ("US_PJM_Philadelphia", 39.95, -75.17),
    ("US_MISO_Chicago", 41.88, -87.63),
    ("US_ISNE_Boston", 42.36, -71.06),
    ("US_SWPP_OklahomaCity", 35.47, -97.52),
    ("US_BPAT_Portland", 45.52, -122.68),
    ("US_SOCO_Atlanta", 33.75, -84.39),
    ("US_AZPS_Phoenix", 33.45, -112.07),
    ("US_PSCO_Denver", 39.74, -104.99),
    ("US_FPL_Miami", 25.76, -80.19),
    ("US_SCL_Seattle", 47.61, -122.33),
    ("US_MISO_Minneapolis", 44.98, -93.27),
    ("US_SWPP_KansasCity", 39.10, -94.58),
    ("US_NEVP_LasVegas", 36.17, -115.14),
    ("US_DUK_Charlotte", 35.23, -80.84),
    ("US_TVA_Nashville", 36.16, -86.78),
    ("DE_Berlin", 52.52, 13.40),
    ("DE_Hamburg", 53.55, 9.99),
    ("DE_Munich", 48.14, 11.58),
    ("FR_Paris", 48.86, 2.35),
    ("ES_Madrid", 40.42, -3.70),
    ("NL_Amsterdam", 52.37, 4.90),
    ("BE_Brussels", 50.85, 4.35),
    ("PL_Warsaw", 52.23, 21.01),
    ("AT_Vienna", 48.21, 16.37),
    ("GB_London", 51.51, -0.13),
    ("GB_Manchester", 53.48, -2.24),
    ("GB_Glasgow", 55.86, -4.25),
    ("AU_NSW1_Sydney", -33.87, 151.21),
    ("AU_QLD1_Brisbane", -27.47, 153.03),
    ("AU_VIC1_Melbourne", -37.81, 144.96),
    ("AU_SA1_Adelaide", -34.93, 138.60),
    ("AU_TAS1_Hobart", -42.88, 147.33),
    ("VN_HoChiMinh", 10.78, 106.70),
    ("VN_HaNoi", 21.03, 105.85),
    ("VN_DaNang", 16.05, 108.20),
]

WEATHER_VARS = [
    "temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature",
    "precipitation", "cloud_cover", "surface_pressure",
    "wind_speed_10m", "wind_speed_100m", "wind_direction_100m", "wind_gusts_10m",
    "shortwave_radiation", "direct_normal_irradiance", "diffuse_radiation",
]
AQ_VARS = ["pm10", "pm2_5", "nitrogen_dioxide", "ozone", "sulphur_dioxide", "carbon_monoxide", "us_aqi"]

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
AQ_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

ERA5_DEFAULT_START = date(2015, 1, 1)   # aligned with ENTSO-E / EIA-930 coverage; ERA5 itself starts 1940
ERA5_EARLIEST = date(1940, 1, 1)
ERA5_LAG_DAYS = 6
AQ_EARLIEST = date(2022, 8, 1)          # start of the global CAMS record served by Open-Meteo
# Open-Meteo counts long/multi-variable requests as several calls (free tier: 600/min, 5000/h, 10000/day).
ARCHIVE_PAUSE = env_int("OPEN_METEO_PAUSE_SECONDS", 30)


def _hourly_frame(payload, location):
    hourly = payload.get("hourly") or {}
    if "time" not in hourly:
        return pd.DataFrame()
    df = pd.DataFrame(hourly)
    df.insert(0, "location", location)
    df["time"] = pd.to_datetime(df["time"], utc=True).dt.strftime("%Y-%m-%dT%H:%MZ")
    return df


def fetch(http, url, loc, lat, lon, variables, **window):
    params = {"latitude": lat, "longitude": lon, "hourly": ",".join(variables), "timezone": "UTC", **window}
    r = check(http.get(url, params=params, timeout=120))
    return _hourly_frame(r.json(), loc)


def collect_recent(http):
    past_days = min(env_int("WEATHER_PAST_DAYS", 3), 92)  # API maximum
    forecast_days = env_int("WEATHER_FORECAST_DAYS", 2)
    now = pd.Timestamp(datetime.now(timezone.utc))
    issued_at = now.floor("h").strftime("%Y-%m-%dT%H:%MZ")
    era5_end = date.today() - timedelta(days=ERA5_LAG_DAYS)
    era5_start = era5_end - timedelta(days=14)

    past, fcst, aq, era5, failures = [], [], [], [], []
    for loc, lat, lon in LOCATIONS:
        try:
            w = fetch(http, WEATHER_URL, loc, lat, lon, WEATHER_VARS, past_days=past_days, forecast_days=forecast_days)
            t = pd.to_datetime(w["time"], utc=True)
            past.append(w[t <= now])
            f = w[t > now].copy()
            f.insert(1, "issued_at", issued_at)
            fcst.append(f)
            a = fetch(http, AQ_URL, loc, lat, lon, AQ_VARS, past_days=past_days, forecast_days=1)
            aq.append(a[pd.to_datetime(a["time"], utc=True) <= now])
            era5.append(fetch(http, ARCHIVE_URL, loc, lat, lon, WEATHER_VARS,
                              start_date=era5_start.isoformat(), end_date=era5_end.isoformat()))
        except Exception as e:  # keep going for the remaining locations
            failures.append(loc)
            print(f"::warning::open-meteo {loc}: {e}")
        time.sleep(0.5)

    upsert(pd.concat(past or [pd.DataFrame()]), "energy/weather/observed", ["location", "time"], "time")
    upsert(pd.concat(fcst or [pd.DataFrame()]), "energy/weather/forecast", ["location", "issued_at", "time"], "issued_at")
    upsert(pd.concat(aq or [pd.DataFrame()]), "energy/airquality/observed", ["location", "time"], "time")
    upsert(_drop_empty(pd.concat(era5 or [pd.DataFrame()])), "energy/weather/era5", ["location", "time"], "time")
    if len(failures) == len(LOCATIONS):
        raise SystemExit("open-meteo: every location failed")


def _drop_empty(df):
    """ERA5 returns null rows for the most recent hours not yet processed."""
    if df.empty:
        return df
    values = [c for c in df.columns if c not in ("location", "time")]
    return df.dropna(subset=values, how="all")


def per_location(chunker):
    return lambda s, e: [
        (f"{cid}/{loc}", first, last, (loc, lat, lon))
        for cid, first, last in chunker(s, e)
        for loc, lat, lon in LOCATIONS
    ]


def history_fetcher(http, url, table, variables):
    def fetch_chunk(first, last, location):
        loc, lat, lon = location
        df = _drop_empty(fetch(http, url, loc, lat, lon, variables,
                               start_date=first.isoformat(), end_date=last.isoformat()))
        time.sleep(ARCHIVE_PAUSE)
        if df.empty:
            raise backfill.Skip("no data returned")
        upsert(df, table, ["location", "time"], "time")
    return fetch_chunk


def main():
    http = session()
    try:
        collect_recent(http)
        error = None
    except SystemExit as e:  # an outage of the live API must not block the history backfill
        error = e
    era5_cap = date.today() - timedelta(days=ERA5_LAG_DAYS)
    backfill.run(
        "energy", "era5", ERA5_DEFAULT_START, ERA5_EARLIEST,
        per_location(lambda s, e: backfill.year_chunks(s, min(e, era5_cap))),
        history_fetcher(http, ARCHIVE_URL, "energy/weather/era5", WEATHER_VARS),
    )
    backfill.run(
        "energy", "airquality", AQ_EARLIEST, AQ_EARLIEST,
        per_location(backfill.year_chunks),
        history_fetcher(http, AQ_URL, "energy/airquality/observed", AQ_VARS),
    )
    if error:
        raise error


if __name__ == "__main__":
    main()
