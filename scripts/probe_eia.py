"""Temporary: align EIA API periods with the six-month bulk files."""
import csv
import io
import os

import requests

KEY = os.environ["EIA_API_KEY"]
r = requests.get("https://api.eia.gov/v2/electricity/rto/region-data/data/", params=[
    ("api_key", KEY), ("frequency", "hourly"), ("data[0]", "value"), ("facets[respondent][]", "CISO"),
    ("facets[type][]", "D"), ("start", "2019-01-02T06"), ("end", "2019-01-02T12"),
    ("sort[0][column]", "period"), ("sort[0][direction]", "asc")], timeout=120)
print("API CISO D:", [(d["period"], d["value"]) for d in r.json()["response"]["data"]])

url = "https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_2019_Jan_Jun.csv"
with requests.get(url, timeout=300, stream=True, headers={"User-Agent": "Mozilla/5.0"}) as resp:
    resp.encoding = "utf-8"
    lines = resp.iter_lines(decode_unicode=True)
    header = next(csv.reader([next(lines)]))
    print("BULK header:", header)
    idx = {h: i for i, h in enumerate(header)}
    shown = 0
    for line in lines:
        row = next(csv.reader([line]))
        if row[0] == "CISO" and row[idx["Data Date"]] == "01/01/2019" and shown < 30:
            shown += 1
            if shown > 20:
                print("BULK CISO:", row[idx["UTC Time at End of Hour"]], row[idx["Demand (MW)"]])
        if row[0] == "CISO" and row[idx["Data Date"]] == "01/02/2019":
            print("BULK CISO:", row[idx["UTC Time at End of Hour"]], row[idx["Demand (MW)"]], "local end", row[idx["Local Time at End of Hour"]])
            shown += 1
        if shown > 34:
            break
