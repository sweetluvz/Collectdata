"""Open-Meteo weather + air quality (no API key).

Two weather tables are stored:
  * weather_*   : latest value per (location, time) over the recent past - use as observed/analysis data.
  * forecast_*  : every forecast issue kept separately (issued_at, time) - lets STLF models be evaluated
                  with the weather forecasts actually available at prediction time.
"""
from datetime import datetime, timezone
import time

import pandas as pd

from utils.http import env_int, session
from utils.storage import upsert

# Near load centres of the EIA balancing authorities, ENTSO-E bidding zones and VN real-estate cities.
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
    ("DE_Berlin", 52.52, 13.40),
    ("DE_Hamburg", 53.55, 9.99),
    ("DE_Munich", 48.14, 11.58),
    ("FR_Paris", 48.86, 2.35),
    ("ES_Madrid", 40.42, -3.70),
    ("NL_Amsterdam", 52.37, 4.90),
    ("BE_Brussels", 50.85, 4.35),
    ("PL_Warsaw", 52.23, 21.01),
    ("AT_Vienna", 48.21, 16.37),
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
AQ_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


def _hourly_frame(payload, location):
    hourly = payload.get("hourly") or {}
    if "time" not in hourly:
        return pd.DataFrame()
    df = pd.DataFrame(hourly)
    df.insert(0, "location", location)
    df["time"] = pd.to_datetime(df["time"], utc=True).dt.strftime("%Y-%m-%dT%H:%MZ")
    return df


def fetch(http, url, loc, lat, lon, variables, past_days, forecast_days):
    params = {
        "latitude": lat, "longitude": lon, "hourly": ",".join(variables), "timezone": "UTC",
        "past_days": past_days, "forecast_days": forecast_days,
    }
    r = http.get(url, params=params, timeout=60)
    r.raise_for_status()
    return _hourly_frame(r.json(), loc)


def main():
    http = session()
    past_days = env_int("WEATHER_PAST_DAYS", 3)
    forecast_days = env_int("WEATHER_FORECAST_DAYS", 2)
    now = pd.Timestamp(datetime.now(timezone.utc))
    issued_at = now.floor("h").strftime("%Y-%m-%dT%H:%MZ")

    past, fcst, aq, failures = [], [], [], []
    for loc, lat, lon in LOCATIONS:
        try:
            w = fetch(http, WEATHER_URL, loc, lat, lon, WEATHER_VARS, past_days, forecast_days)
            t = pd.to_datetime(w["time"], utc=True)
            past.append(w[t <= now])
            f = w[t > now].copy()
            f.insert(1, "issued_at", issued_at)
            fcst.append(f)
            a = fetch(http, AQ_URL, loc, lat, lon, AQ_VARS, past_days, 1)
            aq.append(a[pd.to_datetime(a["time"], utc=True) <= now])
        except Exception as e:  # keep going for the remaining locations
            failures.append(loc)
            print(f"::warning::open-meteo {loc}: {e}")
        time.sleep(0.5)

    upsert(pd.concat(past or [pd.DataFrame()]), "energy", "weather", ["location", "time"], "time", prefix="weather_")
    upsert(pd.concat(fcst or [pd.DataFrame()]), "energy", "weather", ["location", "issued_at", "time"], "issued_at", prefix="forecast_")
    upsert(pd.concat(aq or [pd.DataFrame()]), "energy", "weather", ["location", "time"], "time", prefix="airquality_")

    if len(failures) == len(LOCATIONS):
        raise SystemExit("open-meteo: every location failed")


if __name__ == "__main__":
    main()
