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


def test_eia_paginates_slims_and_backfills_by_month(data_dir, monkeypatch):
    import scrapers.energy.eia_collector as ec

    monkeypatch.setenv("EIA_API_KEY", "k")
    monkeypatch.setattr(ec, "PAGE", 2)
    seen = []

    def fake_get(url, params=None, timeout=None):
        p = dict(params)
        seen.append((p["start"], p["offset"]))
        key = "fueltype" if "fuel" in url else "type"
        day = p["start"][:10]
        rows = [{"period": f"{day}T0{i}", "respondent": "CISO", "respondent-name": "California", key: "D",
                 "type-name": "Demand", "value": "1", "value-units": "MWh"} for i in range(3)]
        return FakeResponse({"response": {"total": "3", "data": rows[p["offset"]:p["offset"] + 2]}})

    with mock.patch("requests.Session.get", side_effect=fake_get):
        ec.main()
    region = load_all("energy/eia/region")
    assert list(region.columns) == ["period", "respondent", "type", "value"]
    assert len(region) == 3

    monkeypatch.setenv("BACKFILL_START", "2015-06-01")
    monkeypatch.setenv("BACKFILL_END", "2015-08-15")
    with mock.patch("requests.Session.get", side_effect=fake_get):
        ec.main()
    state = backfill.load_state("energy")["eia"]
    assert state["start"] == "2015-07-01" and state["done"] == ["2015-07", "2015-08"]
    assert ("2015-07-01T00", 0) in seen and ("2015-08-01T00", 2) in seen


def test_missing_key_skips_without_failing(monkeypatch):
    import scrapers.energy.eia_collector as ec

    monkeypatch.delenv("EIA_API_KEY", raising=False)
    with pytest.raises(SystemExit) as exc:
        ec.main()
    assert exc.value.code == 0
