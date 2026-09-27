import numpy as np
import pandas as pd

from processing import clean, energy, realestate
from processing.io import END, START, load, output_dir, to_hourly_end
from utils.storage import upsert


def hourly(values, start="2024-01-01T01:00Z"):
    return pd.Series(values, index=pd.date_range(start, periods=len(values), freq="1h"), dtype=float)


def daily_shape(n):
    return 1000 + 200 * np.sin(np.arange(n) * 2 * np.pi / 24)


def test_screen_flags_each_check():
    s = hourly(daily_shape(24 * 30))
    s.iloc[100] = -5            # nonpositive
    s.iloc[200:230] = 777.0     # stuck for 30 h
    s.iloc[400] = 1000 * 50     # level (and spike)
    s.iloc[500] = s.iloc[500] + 700  # isolated spike, within level bounds
    cleaned, flags = clean.screen(s)
    assert flags["nonpositive"].iloc[100]
    assert flags["stuck"].iloc[200:230].all() and not flags["stuck"].iloc[199]
    assert flags["level"].iloc[400]
    assert flags["spike"].iloc[500]
    assert cleaned.isna().sum() == flags.any(axis=1).sum()
    assert flags.any(axis=1).sum() < 40  # a clean diurnal cycle is not flagged


def test_fill_short_gaps_keeps_long_gaps():
    s = hourly([1, np.nan, np.nan, 4, 5, np.nan, np.nan, np.nan, np.nan, 10])
    out = clean.fill_short_gaps(s, max_hours=3)
    assert out.iloc[1:3].tolist() == [2, 3]
    assert out.iloc[5:9].isna().all()


def test_to_hourly_end_labels():
    idx = pd.date_range("2024-01-01T00:00Z", periods=8, freq="15min")
    start_stamped = to_hourly_end(pd.DataFrame({"v": range(8)}, index=idx), START)
    assert start_stamped.index[0] == pd.Timestamp("2024-01-01T01:00Z")
    assert start_stamped["v"].iloc[0] == 1.5          # 00:00..00:45 -> hour ending 01:00

    idx = pd.date_range("2024-01-01T00:30Z", periods=4, freq="30min")  # 00:30, 01:00, 01:30, 02:00
    end_stamped = to_hourly_end(pd.DataFrame({"v": [1, 3, 5, 7]}, index=idx), END)
    assert end_stamped.loc["2024-01-01T01:00Z", "v"] == 2  # (00:00, 01:00]
    assert end_stamped.loc["2024-01-01T02:00Z", "v"] == 6


def test_load_filters_months_and_rows():
    df = pd.DataFrame({"timestamp": ["2024-01-01T00:00Z", "2024-01-01T00:00Z", "2024-03-01T00:00Z"],
                       "country": ["de", "fr", "de"], "Load": [1, 2, 3]})
    upsert(df, "energy/europe/power", ["timestamp", "country"], "timestamp")
    got = load("energy/europe/power", "timestamp", "2024-01-01", "2024-01-31", where=("country", ["de"]))
    assert got["Load"].tolist() == [1]


def test_build_us_panel(data_dir):
    periods = pd.date_range("2024-07-01T00:00Z", periods=120, freq="1h")
    d = daily_shape(120)
    region = pd.DataFrame({"period": periods.strftime("%Y-%m-%dT%H"), "ERCO_D": d, "ERCO_DF": d * 1.01,
                           "ERCO_NG": d, "ERCO_TI": 0.0})
    region = region.drop(index=10)  # a missing hour
    upsert(region, "energy/eia/region", ["period"], "period", cellwise=True)
    wx = pd.DataFrame({"time": periods.strftime("%Y-%m-%dT%H:%M"), "location": "US_ERCO_Dallas",
                       "temperature_2m": 30.0})
    upsert(wx, "energy/weather/era5", ["time", "location"], "time")
    report = []
    (path,) = energy.build_us(["ERCO"], report=report)
    panel = pd.read_csv(path, index_col="time")
    assert len(panel) == 120 and panel["demand_raw"].isna().sum() == 1
    assert panel["demand"].notna().all()                 # the 1-hour gap was interpolated
    assert panel["wx_temperature_2m"].eq(30).all()
    # 2024-07-04 is a US federal holiday; hour ending 05:00Z = 23:00 local on 07-03
    assert panel.loc["2024-07-04T05:00Z", "us_holiday"] == 0
    assert panel.loc["2024-07-04T06:00Z", "us_holiday"] == 1
    assert report[0]["area"] == "ERCO" and report[0]["hours"] == 120


def test_build_europe_and_aemo(data_dir):
    stamps = pd.date_range("2024-01-01T00:00Z", periods=4 * 48, freq="15min")
    power = pd.DataFrame({"timestamp": stamps.strftime("%Y-%m-%dT%H:%MZ"), "country": "DE",
                          "Load": np.repeat(daily_shape(48), 4), "Solar": 0.0})
    upsert(power, "energy/europe/power", ["timestamp", "country"], "timestamp", cellwise=True)
    price = pd.DataFrame({"timestamp": stamps[::4].strftime("%Y-%m-%dT%H:%MZ"), "DE-LU": -10.0})
    upsert(price, "energy/europe/price", ["timestamp"], "timestamp", cellwise=True)
    (path,) = energy.build_europe(["DE"])
    panel = pd.read_csv(path, index_col="time")
    assert panel.index[0] == "2024-01-01T01:00Z"
    assert panel["price_eur_mwh"].eq(-10).all()          # negative prices are kept
    assert "load" in panel and "ec_Solar" in panel

    ts = pd.date_range("2024-01-01T00:05Z", periods=12 * 24, freq="5min")
    aemo = pd.DataFrame({"timestamp": ts.strftime("%Y-%m-%dT%H:%MZ"), "NSW1_demand": 8000.0,
                         "NSW1_price": 50.0})
    upsert(aemo, "energy/aemo/price_demand", ["timestamp"], "timestamp", cellwise=True)
    (path,) = energy.build_aemo()
    panel = pd.read_csv(path, index_col="time")
    assert panel.index[0] == "2024-01-01T01:00Z" and len(panel) == 24


def test_clean_chotot_drop_reasons(data_dir):
    rng = np.random.default_rng(0)
    n = 40
    ads = pd.DataFrame({
        "list_id": range(n), "list_time": "2024-05-01T00:00Z", "type": "s",
        "region_v2": 13000, "category": 1010, "size": 70.0,
        "price": 70 * 5e7 * rng.uniform(0.8, 1.2, n), "latitude": 10.8, "longitude": 106.7,
    })
    ads.loc[0, "type"] = "u"
    ads.loc[1, "price"] = 0
    ads.loc[2, "size"] = np.nan
    ads.loc[3, "price"] = 70 * 10          # 10 VND/m2
    ads.loc[4, "latitude"] = np.nan
    ads.loc[5, "price"] = 70 * 5e8         # 10x the median, still inside the absolute bounds
    upsert(ads, "realestate/chotot/ads", ["list_id"], "list_time")
    snaps = pd.DataFrame({"list_id": [6, 6], "price": 1.0, "scraped_date": ["2024-05-01", "2024-05-03"]})
    upsert(snaps, "realestate/chotot/snapshots", ["list_id", "scraped_date"], "scraped_date")
    path, summary = realestate.clean_chotot()
    assert summary["kept"] == n - 6
    for why in ("not_for_sale", "no_price", "no_size", "price_per_m2_implausible", "no_coordinates",
                "price_per_m2_outlier"):
        assert summary[why] == 1, why
    kept = pd.read_csv(path)
    assert kept.loc[kept["list_id"] == 6, "days_seen"].item() == 2
    assert path.parent.parent == output_dir()


def test_quality_report_accumulates(data_dir):
    from processing import build

    s = hourly([1, np.nan, np.nan, 4])
    assert clean.longest_gap(s) == 2
    build.write_report([{"grid": "us", "area": "ERCO", "series": "demand", "hours": 1}], {})
    build.write_report([{"grid": "aemo", "area": "NSW1", "series": "demand", "hours": 2}], {"x": {"kept": 3}})
    build.write_report([{"grid": "us", "area": "ERCO", "series": "demand", "hours": 5}], {})
    q = pd.read_csv(output_dir() / "quality.csv")
    assert sorted(zip(q["area"], q["hours"])) == [("ERCO", 5), ("NSW1", 2)]
    assert "kept: 3" in (output_dir() / "QUALITY.md").read_text()


def test_screen_keeps_real_low_values_when_asked():
    s = hourly(daily_shape(24 * 30))
    s.iloc[300] = -20.0  # midday operational demand under heavy rooftop PV
    _, strict = clean.screen(s)
    _, lenient = clean.screen(s, positive=False, low_level=False)
    assert strict.iloc[300].any() and not lenient.iloc[300][["nonpositive", "level"]].any()
