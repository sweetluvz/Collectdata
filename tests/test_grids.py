import io
import json
from unittest import mock
import zipfile

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


def test_europe_power_and_prices(data_dir, monkeypatch):
    import scrapers.energy.europe_collector as eu

    monkeypatch.setattr(eu, "COUNTRIES", ["de", "fr"])
    monkeypatch.setattr(eu, "BIDDING_ZONES", ["DE-LU", "BAD"])
    ts = [1789862400, 1789863300]

    def get(url, params=None, timeout=None):
        if url.endswith("/price"):
            if params["bzn"] == "BAD":
                return FakeResponse(status=400, text="unknown zone")
            return FakeResponse({"unix_seconds": ts, "price": [80.1, 81.2], "unit": "EUR / MWh"})
        return FakeResponse({"unix_seconds": ts, "production_types": [
            {"name": "Solar", "data": [0.0, 1.5]}, {"name": "Load", "data": [50000, 51000]}]})

    with mock.patch("requests.Session.get", side_effect=get):
        eu.main()
    power = load_all("energy/europe/power")
    assert set(power.country) == {"DE", "FR"} and {"Solar", "Load"} <= set(power.columns)
    assert power.timestamp.iloc[0] == "2026-09-20T00:00Z"
    price = load_all("energy/europe/price")
    assert list(price.columns) == ["timestamp", "DE-LU"] and len(price) == 2


def test_gb_weekly_windows_and_tables(data_dir, monkeypatch):
    import scrapers.energy.gb_collector as gb

    ranges = []

    def get(url, params=None, timeout=None):
        if "carbonintensity" in url:
            return FakeResponse({"data": [{"from": "2026-09-20T00:00Z", "to": "2026-09-20T00:30Z",
                                           "intensity": {"forecast": 60, "actual": 55, "index": "low"}}]})
        ranges.append((params["settlementDateFrom"], params["settlementDateTo"]))
        if "FUELHH" in url:
            return FakeResponse({"data": [
                {"startTime": "2026-09-20T00:00:00Z", "fuelType": f, "generation": g} for f, g in (("WIND", 9000), ("CCGT", 5000))]})
        return FakeResponse({"data": [{"startTime": "2026-09-20T00:00:00Z", "initialDemandOutturn": 19613,
                                       "initialTransmissionSystemDemandOutturn": 25536}]})

    monkeypatch.setenv("BACKFILL_START", "2016-01-01")
    monkeypatch.setenv("BACKFILL_END", "2016-01-20")
    with mock.patch("requests.Session.get", side_effect=get):
        gb.main()
    assert ("2016-01-01", "2016-01-07") in ranges and ("2016-01-15", "2016-01-20") in ranges
    assert all((pd.Timestamp(b) - pd.Timestamp(a)).days <= 6 for a, b in ranges)
    assert list(load_all("energy/gb/generation").columns) == ["timestamp", "CCGT", "WIND"]
    assert list(load_all("energy/gb/demand").columns) == ["timestamp", "indo", "itsdo"]
    assert load_all("energy/gb/carbon_intensity").iloc[0]["actual"] == "55"
    assert backfill.load_state("energy")["gb"]["done"] == ["2016-01"]


def nyiso_csv(day, hours=("00:00", "01:00")):
    lines = ["Time Stamp,Name,PTID,LBMP ($/MWHr),Marginal Cost Losses ($/MWHr),Marginal Cost Congestion ($/MWHr)"]
    for h in hours:
        for zone, price in (("CAPITL", 40.17), ("H Q", 39.35)):
            lines.append(f"{day:%m/%d/%Y} {h},{zone},1,{price},0,0")
    return "\n".join(lines) + "\n"


def test_nyiso_daily_and_monthly_archive(data_dir, monkeypatch):
    import scrapers.energy.nyiso_collector as ny

    def get(url, timeout=None):
        name = url.rsplit("/", 1)[1]
        if name.endswith("_csv.zip"):
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w") as z:
                z.writestr(name[:8] + "damlbmp_zone.csv", nyiso_csv(pd.Timestamp(name[:8])))
            return FakeResponse(content=buf.getvalue())
        return FakeResponse(text=nyiso_csv(pd.Timestamp(name[:8])))

    monkeypatch.setenv("BACKFILL_START", "2015-01-01")
    monkeypatch.setenv("BACKFILL_END", "2015-01-31")
    monkeypatch.setenv("BACKFILL_SOURCES", "nyiso_da")
    with mock.patch("requests.Session.get", side_effect=get):
        ny.main()
    da = load_all("energy/nyiso/lbmp_da")
    assert list(da.columns) == ["timestamp", "CAPITL", "H Q"]
    assert "2015-01-01T05:00Z" in set(da.timestamp)  # midnight EST = 05:00 UTC
    assert not load_all("energy/nyiso/lbmp_rt").empty
    assert backfill.load_state("energy")["nyiso_da"]["done"] == ["2015-01"]


def test_nyiso_dst_fall_back_hour_is_resolved():
    import scrapers.energy.nyiso_collector as ny

    local = pd.Series(["11/01/2026 00:00", "11/01/2026 01:00", "11/01/2026 01:00", "11/01/2026 02:00"])
    utc = ny.to_utc(local).dt.strftime("%H:%M").tolist()
    assert utc == ["04:00", "05:00", "06:00", "07:00"]


def test_chotot_drops_personal_fields_and_snapshots(data_dir, monkeypatch):
    import scrapers.realestate.chotot_collector as ct

    monkeypatch.setattr(ct, "CATEGORIES", {1020: "house"})
    monkeypatch.setattr(ct, "REGIONS", {13000: "hcm"})
    ad = {"list_id": 134925769, "ad_id": 179054592, "list_time": 1790503559000, "category": 1020,
          "price": 3550000000, "size": 30, "rooms": 2, "latitude": 10.779, "longitude": 106.624,
          "account_name": "c trang", "full_name": "Nguyen Van A", "seller_info": {"x": 1},
          "subject": "Nhà hẻm xe hơi LH 0912 345 678", "body": "Sổ hồng riêng " * 100,
          "params": [{"id": "direction", "label": "Hướng", "value": "Hướng Bắc"}], "pty_characteristics": [3, 2]}
    pages = []

    def get(url, params=None, timeout=None):
        pages.append(params["o"])
        return FakeResponse({"ads": [ad] * (ct.PAGE if params["o"] == 0 else 1), "total": 51})

    with mock.patch("requests.Session.get", side_effect=get):
        ct.main()
    assert pages == [0, 50]
    ads = load_all("realestate/chotot/ads")
    assert len(ads) == 1
    row = ads.iloc[0]
    assert not {"account_name", "full_name", "seller_info"} & set(ads.columns)
    assert row.subject == "Nhà hẻm xe hơi LH [SĐT]" and len(row.body) == 500
    assert json.loads(row.params) == {"direction": "Hướng Bắc"} and row.pty_characteristics == "3;2"
    assert row.list_time == "2026-09-27T10:05Z"
    assert len(load_all("realestate/chotot/snapshots")) == 1


def test_gb_survives_null_carbon_answers(data_dir, monkeypatch):
    import scrapers.energy.gb_collector as gb

    def get(url, params=None, timeout=None):
        if "carbonintensity" in url:
            return FakeResponse(None)  # body "null" before the API's record starts
        if "FUELHH" in url:
            return FakeResponse({"data": [{"startTime": "2016-01-01T00:00:00Z", "fuelType": "COAL", "generation": 1}]})
        return FakeResponse({"data": []})

    monkeypatch.setenv("BACKFILL_START", "2016-01-01")
    monkeypatch.setenv("BACKFILL_END", "2016-01-07")
    with mock.patch("requests.Session.get", side_effect=get):
        gb.main()
    assert backfill.load_state("energy")["gb"]["done"] == ["2016-01"]


def test_aemo_reads_old_files_without_seconds(data_dir):
    import scrapers.energy.aemo_collector as ae

    text = 'REGION,SETTLEMENTDATE,TOTALDEMAND,RRP,PERIODTYPE\nNSW1,"1998/12/07 02:00",5000,20,TRADE\n'
    with mock.patch("requests.Session.get", return_value=FakeResponse(text=text)):
        df = ae.fetch_month(ae.session(), 1998, 12)
    assert df.timestamp.tolist() == ["1998-12-06T16:00Z"]
