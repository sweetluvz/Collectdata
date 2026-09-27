from unittest import mock

import pandas as pd
import pytest

from conftest import FakeResponse
from utils.storage import load_all


def test_weather_splits_observed_and_forecast(data_dir):
    import scrapers.energy.weather_collector as wc

    now = pd.Timestamp.now(tz="UTC").floor("h")
    times = pd.date_range(now - pd.Timedelta("24h"), now + pd.Timedelta("24h"), freq="h").strftime("%Y-%m-%dT%H:%M")

    def fake_get(url, params=None, timeout=None):
        return FakeResponse({"hourly": {"time": list(times), **{v: [1.0] * len(times) for v in params["hourly"].split(",")}}})

    with mock.patch.object(wc, "LOCATIONS", wc.LOCATIONS[:2]), mock.patch("requests.Session.get", side_effect=fake_get):
        wc.main()

    observed = load_all("energy/weather/observed")
    forecast = load_all("energy/weather/forecast")
    assert set(observed.location) == {"US_CISO_LosAngeles", "US_CISO_SanFrancisco"}
    assert (pd.to_datetime(observed.time) <= now).all()
    assert (pd.to_datetime(forecast.time) > pd.to_datetime(forecast.issued_at)).all()
    assert not load_all("energy/airquality/observed").empty


def test_eia_paginates_and_writes_both_tables(data_dir, monkeypatch):
    import scrapers.energy.eia_collector as ec

    monkeypatch.setenv("EIA_API_KEY", "k")
    monkeypatch.setattr(ec, "PAGE", 2)
    offsets = []

    def fake_get(url, params=None, timeout=None):
        offset = dict(params)["offset"]
        offsets.append(offset)
        key = "fueltype" if "fuel" in url else "type"
        rows = [{"period": f"2026-09-26T0{i}", "respondent": "CISO", key: "D", "value": "1"} for i in range(3)]
        return FakeResponse({"response": {"total": "3", "data": rows[offset:offset + 2]}})

    with mock.patch("requests.Session.get", side_effect=fake_get):
        ec.main()
    assert offsets == [0, 2, 0, 2]
    assert len(load_all("energy/eia/region")) == 3
    assert len(load_all("energy/eia/fuel_type")) == 3


def test_missing_key_skips_without_failing(monkeypatch):
    import scrapers.energy.eia_collector as ec

    monkeypatch.delenv("EIA_API_KEY", raising=False)
    with pytest.raises(SystemExit) as exc:
        ec.main()
    assert exc.value.code == 0


def test_entsoe_long_format_and_one_table_per_dataset(data_dir, monkeypatch):
    import scrapers.energy.entsoe_collector as en

    idx = pd.date_range("2026-09-26", periods=2, freq="h", tz="Europe/Brussels")
    gen = pd.DataFrame(
        [[1, 2], [3, 4]], index=idx,
        columns=pd.MultiIndex.from_tuples([("Solar", "Actual Aggregated"), ("Hydro", "Actual Consumption")]),
    )
    long = en.to_long(gen, "DE_LU", "generation")
    assert set(long.variable) == {"Solar | Actual Aggregated", "Hydro | Actual Consumption"}
    assert long.timestamp.iloc[0] == "2026-09-25T22:00Z"

    class FakeClient:
        def __init__(self, api_key):
            pass

        def query_load(self, *a, **k):
            return pd.DataFrame({"Actual Load": [1.0, 2.0]}, index=idx)

        def query_day_ahead_prices(self, *a, **k):
            return pd.Series([50.0, None], index=idx)

        def __getattr__(self, name):
            def fail(*a, **k):
                raise RuntimeError("NoMatchingDataError")
            return fail

    monkeypatch.setenv("ENTSOE_API_KEY", "k")
    with mock.patch.object(en, "EntsoePandasClient", FakeClient):
        en.main()
    assert len(load_all("energy/entsoe/load")) == 2 * len(en.ZONES)
    assert len(load_all("energy/entsoe/day_ahead_price")) == len(en.ZONES)
