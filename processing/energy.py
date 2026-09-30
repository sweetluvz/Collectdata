"""Analysis-ready hourly panels: load (screened) + benchmark forecast + weather + calendar, per grid area.

Outputs processed/<grid>/<area>.csv.gz, one row per hour (UTC, labelled at the end of the hour).
"""
import functools

import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

from processing import clean
from processing.io import END, START, load, output_dir, to_hourly_end

WEATHER_COLS = ["temperature_2m", "relative_humidity_2m", "dew_point_2m", "cloud_cover", "precipitation",
                "wind_speed_10m", "wind_speed_100m", "shortwave_radiation"]

US_TZ = {
    "CISO": "America/Los_Angeles", "BPAT": "America/Los_Angeles", "SCL": "America/Los_Angeles",
    "NEVP": "America/Los_Angeles", "AZPS": "America/Phoenix", "PSCO": "America/Denver",
    "ERCO": "America/Chicago", "MISO": "America/Chicago", "SWPP": "America/Chicago", "TVA": "America/Chicago",
    "NYIS": "America/New_York", "PJM": "America/New_York", "ISNE": "America/New_York",
    "SOCO": "America/New_York", "FPL": "America/New_York", "DUK": "America/New_York",
}
EU_TZ = "Europe/Berlin"
EU_PRICE_ZONE = {"DE": "DE-LU", "FR": "FR", "ES": "ES", "NL": "NL", "BE": "BE", "AT": "AT", "PL": "PL",
                 "CH": "CH", "DK": "DK1", "IT": "IT-North"}
AEMO_REGIONS = ["NSW1", "QLD1", "VIC1", "SA1", "TAS1"]


@functools.lru_cache(maxsize=2)
def _era5(start, end):
    """ERA5 is read once per build instead of once per area (it is the largest table)."""
    return load("energy/weather/era5", "time", start, end, columns=WEATHER_COLS + ["location"])


def weather_for(token, start, end, prefix=None):
    """Mean ERA5 weather over the locations whose code contains `token` (e.g. ERCO, NSW1) or starts with prefix."""
    df = _era5(start, end)
    if df.empty:
        return pd.DataFrame()
    parts = df["location"].str.split("_")
    mask = parts.str[0].eq(prefix) if prefix else parts.apply(lambda p: token in p)
    sel = df[mask].drop(columns="location")
    return sel.groupby(level=0).mean().add_prefix("wx_") if not sel.empty else pd.DataFrame()


def calendar(index, tz, holidays=False):
    local = (index - pd.Timedelta(hours=1)).tz_convert(tz)  # hour-ending label -> local start of the hour
    cal = pd.DataFrame({
        "local_hour": local.hour, "local_dow": local.dayofweek, "local_month": local.month,
    }, index=index)
    if holidays:
        days = USFederalHolidayCalendar().holidays(local.min().date(), local.max().date())
        cal["us_holiday"] = pd.Index(local.normalize().tz_localize(None)).isin(days).astype(int)
    return cal


def screened(series, name, report, area, **kw):
    raw = pd.to_numeric(series, errors="coerce")
    cleaned, flags = clean.screen(raw, **kw)
    report.append({"area": area, "series": name, **clean.quality(raw, cleaned, flags)})
    return cleaned, flags


def _save(frame, grid, area):
    path = output_dir() / grid / f"{area}.csv.gz"
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.index = frame.index.strftime("%Y-%m-%dT%H:%MZ")
    frame.index.name = "time"
    frame.to_csv(path, compression={"method": "gzip", "mtime": 0})
    return path


def full_hours(index):
    return pd.date_range(index.min(), index.max(), freq="1h") if len(index) else index


def build_us(bas, start=None, end=None, report=None, max_gap=3):
    report = [] if report is None else report
    cols = [f"{ba}_{t}" for ba in bas for t in ("D", "DF", "NG", "TI")]
    region = load("energy/eia/region", "period", start, end, columns=cols)  # EIA periods are hour-ending already
    out = []
    for ba in bas:
        if f"{ba}_D" not in region:
            print(f"[us] {ba}: no demand column, skipped")
            continue
        df = region[[c for c in region if c.startswith(f"{ba}_")]].apply(pd.to_numeric, errors="coerce")
        df = df.reindex(full_hours(df[f"{ba}_D"].dropna().index))
        demand, flags = screened(df[f"{ba}_D"], "demand", report, ba)
        forecast, _ = screened(df.get(f"{ba}_DF", pd.Series(index=df.index, dtype=float)), "eia_forecast", report, ba)
        panel = pd.DataFrame({
            "demand_raw": df[f"{ba}_D"],
            "demand": clean.fill_short_gaps(demand, max_gap),
            "demand_flags": flags.apply(lambda r: ";".join(r.index[r]), axis=1),
            "eia_dayahead_forecast": forecast,
            "net_generation": df.get(f"{ba}_NG"),
            "interchange": df.get(f"{ba}_TI"),
        }, index=df.index)
        panel = panel.join(weather_for(ba, start, end)).join(calendar(panel.index, US_TZ.get(ba, "UTC"), holidays=True))
        out.append(_save(panel, "us", ba))
        print(f"[us] {ba}: {len(panel):,} hours -> {out[-1]}")
    return out


def build_europe(countries, start=None, end=None, report=None, max_gap=3):
    report = [] if report is None else report
    price = load("energy/europe/price", "timestamp", start, end)
    price = to_hourly_end(price, START) if not price.empty else price
    out = []
    for cc in countries:
        power = load("energy/europe/power", "timestamp", start, end, where=("country", [cc]))
        if power.empty:
            print(f"[europe] {cc}: no data, skipped")
            continue
        hourly = to_hourly_end(power.drop(columns="country"), START)  # 15-min interval-start stamps
        hourly = hourly.reindex(full_hours(hourly.index)).dropna(axis=1, how="all")
        panel = hourly.add_prefix("ec_")  # Energy-Charts columns as published: MW, except the "share" columns (%)
        if "Load" in hourly:
            load_clean, flags = screened(hourly["Load"], "load", report, cc)
            panel["load"] = clean.fill_short_gaps(load_clean, max_gap)
            panel["load_flags"] = flags.apply(lambda r: ";".join(r.index[r]), axis=1)
        zone = EU_PRICE_ZONE.get(cc)
        if zone and zone in price:
            panel["price_eur_mwh"] = price[zone]  # prices are not screened: negative and extreme prices are real
        panel = panel.join(weather_for(None, start, end, prefix=cc)).join(calendar(panel.index, EU_TZ))
        out.append(_save(panel, "europe", cc))
        print(f"[europe] {cc}: {len(panel):,} hours -> {out[-1]}")
    return out


def build_aemo(start=None, end=None, report=None, max_gap=3):
    report = [] if report is None else report
    raw = load("energy/aemo/price_demand", "timestamp", start, end)
    if raw.empty:
        return []
    hourly = to_hourly_end(raw, END)  # 5/30-min interval-end stamps
    out = []
    for region in AEMO_REGIONS:
        if f"{region}_demand" not in hourly:
            continue
        # operational demand excludes rooftop PV and dips to or below zero at midday in SA1 (and VIC1): real
        demand, flags = screened(hourly[f"{region}_demand"], "demand", report, region, positive=False, low_level=False)
        panel = pd.DataFrame({
            "demand_raw": hourly[f"{region}_demand"],
            "demand": clean.fill_short_gaps(demand, max_gap),
            "demand_flags": flags.apply(lambda r: ";".join(r.index[r]), axis=1),
            "price_aud_mwh": hourly.get(f"{region}_price"),
        }, index=hourly.index)
        panel = panel.join(weather_for(region, start, end)).join(calendar(panel.index, "Australia/Brisbane"))
        out.append(_save(panel, "aemo", region))
        print(f"[aemo] {region}: {len(panel):,} hours -> {out[-1]}")
    return out
