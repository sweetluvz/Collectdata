from datetime import date
from unittest import mock

import pandas as pd
import pytest

from conftest import FakeResponse
from utils import backfill
from utils.storage import load_all


@pytest.fixture(autouse=True)
def no_backfill_env(monkeypatch):
    monkeypatch.setattr(backfill, "_deadline", None)
    for var in ("BACKFILL_START", "BACKFILL_END", "BACKFILL_SOURCES"):
        monkeypatch.delenv(var, raising=False)


def hourly_payload(times, variables):
    return FakeResponse({"hourly": {"time": list(times), **{v: [1.0] * len(times) for v in variables}}})


def test_weather_splits_observed_forecast_and_era5(data_dir):
    import scrapers.energy.weather_collector as wc

    now = pd.Timestamp.now(tz="UTC").floor("h")
    recent = pd.date_range(now - pd.Timedelta("24h"), now + pd.Timedelta("24h"), freq="h").strftime("%Y-%m-%dT%H:%M")
    era5 = pd.date_range(now - pd.Timedelta("20D"), now - pd.Timedelta("6D"), freq="h").strftime("%Y-%m-%dT%H:%M")

    def fake_get(url, params=None, timeout=None):
        times = era5 if "archive" in url else recent
        return hourly_payload(times, params["hourly"].split(","))

    with mock.patch.object(wc, "LOCATIONS", wc.LOCATIONS[:2]), mock.patch("requests.Session.get", side_effect=fake_get):
        wc.main()

    observed = load_all("energy/weather/observed")
    forecast = load_all("energy/weather/forecast")
    assert set(observed.location) == {"US_CISO_LosAngeles", "US_CISO_SanFrancisco"}
    assert (pd.to_datetime(observed.time) <= now).all()
    assert (pd.to_datetime(forecast.time) > pd.to_datetime(forecast.issued_at)).all()
    assert not load_all("energy/airquality/observed").empty
    assert len(load_all("energy/weather/era5")) == 2 * len(era5)


def test_weather_backfill_chunks_per_location_year(data_dir, monkeypatch):
    import scrapers.energy.weather_collector as wc

    monkeypatch.setenv("BACKFILL_START", "2016-12-31")
    monkeypatch.setenv("BACKFILL_END", "2017-01-01")
    monkeypatch.setenv("BACKFILL_SOURCES", "era5")
    requests_seen = []

    def fake_get(url, params=None, timeout=None):
        if "start_date" in params:
            requests_seen.append((params["latitude"], params["start_date"], params["end_date"]))
            times = pd.date_range(params["start_date"], params["end_date"] + " 23:00", freq="h")
        else:
            times = pd.date_range(pd.Timestamp.now().floor("h"), periods=3, freq="h")
        return hourly_payload(times.strftime("%Y-%m-%dT%H:%M"), params["hourly"].split(","))

    with mock.patch.object(wc, "LOCATIONS", wc.LOCATIONS[:2]), mock.patch.object(wc, "ARCHIVE_PAUSE", 0), \
         mock.patch("requests.Session.get", side_effect=fake_get):
        wc.main()

    state = backfill.load_state("energy")["era5"]
    assert state["total"] == 4 and len(state["done"]) == 4
    era5 = load_all("energy/weather/era5")
    assert set(era5.time.str[:7]) >= {"2016-12", "2017-01"}
    assert (data_dir / "energy/weather/era5/2016-12.csv.gz").exists()
    assert ("34.05", "2016-12-31", "2016-12-31") in {(str(a), b, c) for a, b, c in requests_seen}


def test_weather_backfill_runs_even_if_live_api_is_down(data_dir, monkeypatch):
    import scrapers.energy.weather_collector as wc

    monkeypatch.setenv("BACKFILL_START", "2017-01-01")
    monkeypatch.setenv("BACKFILL_END", "2017-01-01")
    monkeypatch.setenv("BACKFILL_SOURCES", "era5")

    def fake_get(url, params=None, timeout=None):
        if params.get("start_date") == "2017-01-01":
            return hourly_payload(pd.date_range("2017-01-01", periods=24, freq="h").strftime("%Y-%m-%dT%H:%M"),
                                  params["hourly"].split(","))
        return FakeResponse(status=503, text="down")

    with mock.patch.object(wc, "LOCATIONS", wc.LOCATIONS[:1]), mock.patch.object(wc, "ARCHIVE_PAUSE", 0), \
         mock.patch("requests.Session.get", side_effect=fake_get), pytest.raises(SystemExit):
        wc.main()
    assert len(load_all("energy/weather/era5")) == 24


def fake_eia(seen, page):
    def fake_get(url, params=None, timeout=None):
        p = dict(params)
        seen.append((url.split("/v2/")[1].rsplit("/data/", 1)[0], p["start"], p["offset"]))
        day = p["start"][:10]
        if "pri/" in url:
            rows = [{"period": day, "series": "RNGWHHD", "series-description": "Henry Hub", "value": "2.5",
                     "units": "$/MMBTU"}]
        elif "retail-sales" in url:
            rows = [{"period": p["start"][:7], "stateid": "CA", "sectorid": "RES", "price": "30.1",
                     "revenue": "1", "sales": "2", "customers": "3"}]
        else:
            base = {"period": f"{day}T01", "value": "1", "value-units": "MWh"}
            if "region-data" in url:
                rows = [{**base, "respondent": r, "type": t} for r in ("CISO", "ERCO") for t in ("D", "NG")]
            elif "fuel-type" in url:
                rows = [{**base, "respondent": "CISO", "fueltype": f} for f in ("SUN", "WND")]
            elif "interchange" in url:
                rows = [{**base, "fromba": "CISO", "toba": "BPAT"}]
            else:
                rows = [{**base, "parent": "ERCO", "subba": "COAS"}]
        return FakeResponse({"response": {"total": str(len(rows)), "data": rows[p["offset"]:p["offset"] + page]}})
    return fake_get


def test_eia_wide_tables_pagination_and_backfill(data_dir, monkeypatch):
    import scrapers.energy.eia_collector as ec

    monkeypatch.setenv("EIA_API_KEY", "k")
    monkeypatch.setattr(ec, "PAGE", 3)
    seen = []
    with mock.patch("requests.Session.get", side_effect=fake_eia(seen, 3)):
        ec.main()
    region = load_all("energy/eia/region")
    assert list(region.columns) == ["period", "CISO_D", "CISO_NG", "ERCO_D", "ERCO_NG"] and len(region) == 1
    assert list(load_all("energy/eia/fuel_type").columns) == ["period", "CISO_SUN", "CISO_WND"]
    assert list(load_all("energy/eia/interchange").columns) == ["period", "CISO>BPAT"]
    assert list(load_all("energy/eia/subregion").columns) == ["period", "ERCO_COAS"]
    prices = load_all("energy/eia/fuel_prices")
    assert list(prices.columns) == ["period", "series", "description", "units", "value"]
    assert list(load_all("energy/eia/retail_sales").columns) == [
        "period", "stateid", "sectorid", "price", "revenue", "sales", "customers"]
    assert ("electricity/rto/region-data", seen[0][1], 3) in seen  # second page requested

    monkeypatch.setenv("BACKFILL_START", "2015-06-01")
    monkeypatch.setenv("BACKFILL_END", "2015-08-15")
    with mock.patch("requests.Session.get", side_effect=fake_eia(seen, 3)):
        ec.main()
    state = backfill.load_state("energy")
    assert state["eia"]["start"] == "2015-07-01" and state["eia"]["done"] == ["2015-07", "2015-08"]
    assert state["eia_market"]["start"] == "2015-06-01"
    assert ("electricity/rto/interchange-data", "2015-08-01T00", 0) in seen
    assert (data_dir / "energy/eia/region/2015-07.csv.gz").exists()


def test_missing_key_skips_without_failing(monkeypatch):
    import scrapers.energy.eia_collector as ec

    monkeypatch.delenv("EIA_API_KEY", raising=False)
    with pytest.raises(SystemExit) as exc:
        ec.main()
    assert exc.value.code == 0


def test_aemo_wide_utc_and_backfill(data_dir, monkeypatch):
    import scrapers.energy.aemo_collector as ae

    def get(url, timeout=None):
        region = url.rsplit("_", 1)[1].removesuffix(".csv")
        if region == "TAS1":
            return FakeResponse(status=404, text="missing")
        ym = url.split("PRICE_AND_DEMAND_")[1][:6]
        text = ("REGION,SETTLEMENTDATE,TOTALDEMAND,RRP,PERIODTYPE\n"
                f'{region},"{ym[:4]}/{ym[4:]}/01 10:30:00",6920.94,48.06,TRADE\n')
        return FakeResponse(text=text)

    monkeypatch.setenv("BACKFILL_START", "auto")
    monkeypatch.setenv("BACKFILL_END", "1999-01-31")
    monkeypatch.setenv("BACKFILL_SOURCES", "aemo")
    with mock.patch("requests.Session.get", side_effect=get):
        ae.main()
    df = load_all("energy/aemo/price_demand")
    assert {"NSW1_demand", "NSW1_price", "SA1_price"} <= set(df.columns) and "TAS1_price" not in df.columns
    assert "1998-12-01T00:30Z" in set(df.timestamp)  # 10:30 NEM time = 00:30 UTC
    state = backfill.load_state("energy")["aemo"]
    assert state["start"] == "1998-12-01" and state["done"] == ["1998-12", "1999-01"]
