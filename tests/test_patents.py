import json
from unittest import mock

from conftest import FakeResponse
from utils.storage import load_all

PATENT = {
    "patent_id": "12000001", "patent_title": "NN controller", "patent_abstract": "abs",
    "patent_date": "2026-09-22", "patent_type": "utility", "patent_num_claims": 20,
    "application": [{"filing_date": "2024-01-02"}],
    "cpc_current": [
        {"cpc_subclass_id": "G06N", "cpc_group_id": "G06N3/08"},
        {"cpc_subclass_id": "G05B", "cpc_group_id": "G05B13/02"},
    ],
    "ipcr": [{"ipc_section": "G", "ipc_class": "06", "ipc_subclass": "N"}],
    "assignees": [{"assignee_organization": "ACME", "assignee_country": "US"}],
    "inventors": [{"inventor_country": "VN"}],
}
LENS = {
    "lens_id": "000-111", "jurisdiction": "WO", "doc_number": "2026123456", "kind": "A1",
    "date_published": "2026-09-24",
    "biblio": {
        "invention_title": [{"text": "Titre", "lang": "fr"}, {"text": "Laser lens", "lang": "en"}],
        "classifications_cpc": {"classifications": [{"symbol": "H01S3/00"}, {"symbol": "G02B1/00"}]},
        "application_reference": {"date": "2025-03-01"},
        "parties": {"applicants": [{"extracted_name": {"value": "Optix"}, "residence": "DE"}]},
    },
    "abstract": [{"text": "An optical...", "lang": "en"}],
    "claims": [{"lang": "en", "claims": [{"claim_text": ["1. A lens comprising..."]}, {"claim_text": ["2. The lens"]}]}],
    "families": {"simple_family": {"size": 3}},
}


def test_uspto_paginates_with_cursor(data_dir, monkeypatch):
    import scrapers.patents.uspto_collector as us

    monkeypatch.setenv("PATENTSVIEW_API_KEY", "k")
    monkeypatch.setattr(us, "PAGE", 1)
    opts = []

    def get(url, params=None, timeout=None):
        opts.append(json.loads(params["o"]))
        return FakeResponse({"patents": [PATENT] if len(opts) == 1 else []})

    with mock.patch("requests.Session.get", side_effect=get):
        us.main()
    assert opts == [{"size": 1}, {"size": 1, "after": "12000001"}]
    row = load_all("patents/uspto/grants", ext=".csv.gz").iloc[0]
    assert (row.cpc_subclasses, row.ipc, row.filing_date) == ("G06N;G05B", "G06N", "2024-01-02")


def test_lens_flattens_and_scrolls(data_dir, monkeypatch):
    import scrapers.patents.lens_collector as lc

    monkeypatch.setenv("LENS_API_TOKEN", "k")
    bodies = []

    def post(url, json=None, timeout=None):
        bodies.append(json)
        if len(bodies) == 1:
            return FakeResponse({"total": 1, "data": [LENS], "scroll_id": "s1"})
        return FakeResponse({"total": 1, "data": [], "scroll_id": None})

    with mock.patch("requests.Session.post", side_effect=post):
        lc.main()
    must = bodies[0]["query"]["bool"]["must"]
    assert {"terms": {"jurisdiction": ["WO", "EP", "US"]}} in must
    assert bodies[1] == {"scroll_id": "s1", "scroll": "1m"}
    row = load_all("patents/lens/publications", ext=".csv.gz").iloc[0]
    assert (row.title, row.first_claim, row.num_claims, row.cpc) == (
        "Laser lens", "1. A lens comprising...", "2", "H01S3/00;G02B1/00")
