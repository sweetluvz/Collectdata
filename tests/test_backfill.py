from datetime import date

import pytest
import requests

from utils import backfill


@pytest.fixture(autouse=True)
def fresh_deadline(monkeypatch):
    monkeypatch.setattr(backfill, "_deadline", None)
    for var in ("BACKFILL_START", "BACKFILL_END", "BACKFILL_SOURCES"):
        monkeypatch.delenv(var, raising=False)


def test_month_and_year_chunks_clip_to_range():
    assert backfill.month_chunks(date(2015, 7, 15), date(2015, 9, 2)) == [
        ("2015-07", date(2015, 7, 15), date(2015, 7, 31)),
        ("2015-08", date(2015, 8, 1), date(2015, 8, 31)),
        ("2015-09", date(2015, 9, 1), date(2015, 9, 2)),
    ]
    assert backfill.year_chunks(date(2015, 3, 1), date(2016, 2, 1)) == [
        ("2015", date(2015, 3, 1), date(2015, 12, 31)),
        ("2016", date(2016, 1, 1), date(2016, 2, 1)),
    ]


def test_plan_resumes_across_runs_and_skips_missing_data(data_dir, monkeypatch):
    calls = []

    def fetch(first, last):
        calls.append(first.strftime("%Y-%m"))
        if first.month == 2:
            raise backfill.Skip("empty")
        if first.month == 3 and calls.count("2020-03") == 1:
            raise requests.ConnectionError("temporary")

    monkeypatch.setenv("BACKFILL_START", "auto")
    monkeypatch.setenv("BACKFILL_END", "2020-04-30")
    backfill.run("energy", "src", date(2020, 1, 1), date(2019, 1, 1), backfill.month_chunks, fetch)
    state = backfill.load_state("energy")["src"]
    assert (state["done"], state["skipped"], state["total"]) == (["2020-01"], ["2020-02"], 4)

    monkeypatch.delenv("BACKFILL_START")  # a later scheduled run continues the stored plan
    backfill.run("energy", "src", date(2020, 1, 1), date(2019, 1, 1), backfill.month_chunks, fetch)
    state = backfill.load_state("energy")["src"]
    assert state["done"] == ["2020-01", "2020-03", "2020-04"]
    assert calls == ["2020-01", "2020-02", "2020-03", "2020-03", "2020-04"]


def test_http_400_is_skipped_but_rate_limit_stops(data_dir, monkeypatch):
    def http_error(status):
        resp = requests.Response()
        resp.status_code = status
        return requests.HTTPError(response=resp)

    def fetch(first, last):
        raise http_error(400 if first.month == 1 else 429)

    monkeypatch.setenv("BACKFILL_START", "2020-01-01")
    monkeypatch.setenv("BACKFILL_END", "2020-03-31")
    backfill.run("energy", "src", date(2020, 1, 1), date(2020, 1, 1), backfill.month_chunks, fetch)
    state = backfill.load_state("energy")["src"]
    assert state["skipped"] == ["2020-01"] and state["done"] == []


def test_time_budget_flags_incomplete(data_dir, monkeypatch, tmp_path):
    flag = tmp_path / "flag"
    monkeypatch.setenv("BACKFILL_FLAG", str(flag))
    monkeypatch.setenv("BACKFILL_START", "2020-01-01")
    monkeypatch.setenv("BACKFILL_END", "2020-12-31")
    monkeypatch.setattr(backfill, "_deadline", 0)  # already expired
    backfill.run("energy", "src", date(2020, 1, 1), date(2020, 1, 1), backfill.month_chunks, lambda f, l: None)
    assert flag.read_text() == "src\n"


def test_sources_filter_and_earliest_bound(data_dir, monkeypatch):
    monkeypatch.setenv("BACKFILL_START", "2000-01-01")
    monkeypatch.setenv("BACKFILL_END", "2015-08-31")
    monkeypatch.setenv("BACKFILL_SOURCES", "eia")
    backfill.run("energy", "era5", date(2015, 1, 1), date(2015, 1, 1), backfill.month_chunks, lambda f, l: None)
    backfill.run("energy", "eia", date(2015, 7, 1), date(2015, 7, 1), backfill.month_chunks, lambda f, l: None)
    state = backfill.load_state("energy")
    assert "era5" not in state
    assert state["eia"]["start"] == "2015-07-01" and state["eia"]["done"] == ["2015-07", "2015-08"]


def test_plan_is_registered_even_without_api_key(data_dir, monkeypatch):
    import scrapers.energy.eia_collector as ec

    monkeypatch.delenv("EIA_API_KEY", raising=False)
    monkeypatch.setenv("BACKFILL_START", "auto")
    with pytest.raises(SystemExit):
        ec.main()
    plan = backfill.load_state("energy")["eia"]
    assert plan["start"] == "2015-07-01" and plan["done"] == []


def test_prune_drops_plans_of_retired_sources(data_dir):
    backfill.save_state("energy", {"eia": {"start": "2015-07-01"}, "entsoe": {"start": "2015-01-01"}})
    assert backfill.prune("energy") == {"entsoe"}
    assert set(backfill.load_state("energy")) == {"eia"}


def test_sources_without_plan_get_default_history_automatically(data_dir, monkeypatch):
    monkeypatch.setenv("BACKFILL_AUTO", "1")
    backfill.register("energy", "aemo", date(1998, 12, 1), date(1998, 12, 1))
    plan = backfill.load_state("energy")["aemo"]
    assert plan["start"] == "1998-12-01" and plan["end"] == date.today().isoformat()

    backfill.save_state("energy", {"aemo": {**plan, "start": "2020-01-01"}})
    backfill.register("energy", "aemo", date(1998, 12, 1), date(1998, 12, 1))  # existing plan left alone
    assert backfill.load_state("energy")["aemo"]["start"] == "2020-01-01"
