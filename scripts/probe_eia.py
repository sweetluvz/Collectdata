"""Temporary: why does EIA return nothing before 2019?"""
import json
import os

import requests

KEY = os.environ["EIA_API_KEY"]
BASE = "https://api.eia.gov/v2/electricity/rto"
for route in ("region-data", "fuel-type-data", "interchange-data", "region-sub-ba-data"):
    for start, end in (("2016-01-01T00", "2016-01-31T23"), ("2018-12-01T00", "2018-12-31T23"), ("2019-01-01T00", "2019-01-01T23")):
        r = requests.get(f"{BASE}/{route}/data/", params={"api_key": KEY, "frequency": "hourly", "data[0]": "value",
                                                        "start": start, "end": end, "length": 1}, timeout=120)
        body = r.text.replace(KEY, "***")
        try:
            js = r.json()
            body = json.dumps({"total": js.get("response", {}).get("total"), "data": js.get("response", {}).get("data"),
                               "error": js.get("error"), "warnings": js.get("warnings")})[:400]
        except ValueError:
            body = body[:300]
        print(f"{route} {start}: HTTP {r.status_code} {body}")
for freq in ("local-hourly",):
    r = requests.get(f"{BASE}/region-data/data/", params={"api_key": KEY, "frequency": freq, "data[0]": "value",
                                                        "start": "2016-01-01T00-05", "end": "2016-01-01T23-05", "length": 1}, timeout=120)
    print(freq, r.status_code, r.text.replace(KEY, "***")[:400])
for name in ("EIA930_BALANCE_2016_Jan_Jun.csv", "EIA930_INTERCHANGE_2016_Jan_Jun.csv", "EIA930_SUBREGION_2019_Jan_Jun.csv"):
    url = f"https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/{name}"
    r = requests.get(url, timeout=120, stream=True, headers={"User-Agent": "Mozilla/5.0"})
    head = next(r.iter_content(600), b"")[:600].decode("utf-8", "replace").replace("\n", " | ")
    print(f"{name}: HTTP {r.status_code} len={r.headers.get('Content-Length')} {head}")
    r.close()
