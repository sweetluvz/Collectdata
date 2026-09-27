"""USPTO granted patents via the PatentsView PatentSearch API.

Free key: https://patentsview-support.atlassian.net/servicedesk (request API key) -> secret PATENTSVIEW_API_KEY
PatentsView refreshes its database roughly quarterly, so each run re-queries a long window and upserts.
"""
from datetime import date, timedelta
import json
import time

import pandas as pd

from scrapers.patents.common import CPC_SUBCLASSES
from utils.http import env_int, require_env, session
from utils.storage import upsert

URL = "https://search.patentsview.org/api/v1/patent/"
FIELDS = [
    "patent_id", "patent_title", "patent_abstract", "patent_date", "patent_type", "patent_num_claims",
    "application", "cpc_current", "ipcr", "assignees", "inventors",
]
PAGE = 1000


def _collect(items, key):
    vals = []
    for it in items or []:
        v = it.get(key) if isinstance(it, dict) else None
        if v and v not in vals:
            vals.append(str(v))
    return ";".join(vals)


def flatten(p):
    app = (p.get("application") or [{}])
    app = app[0] if isinstance(app, list) and app else (app if isinstance(app, dict) else {})
    ipcr = p.get("ipcr") or []
    return {
        "patent_id": p.get("patent_id"),
        "patent_date": p.get("patent_date"),
        "filing_date": app.get("filing_date", ""),
        "patent_type": p.get("patent_type"),
        "title": p.get("patent_title"),
        "abstract": p.get("patent_abstract"),
        "num_claims": p.get("patent_num_claims"),
        "cpc_subclasses": _collect(p.get("cpc_current"), "cpc_subclass_id"),
        "cpc_groups": _collect(p.get("cpc_current"), "cpc_group_id"),
        "ipc": ";".join(
            dict.fromkeys(
                f"{i.get('ipc_section', '')}{i.get('ipc_class', '')}{i.get('ipc_subclass', '')}" for i in ipcr
            )
        ),
        "assignees": _collect(p.get("assignees"), "assignee_organization"),
        "assignee_countries": _collect(p.get("assignees"), "assignee_country"),
        "inventor_countries": _collect(p.get("inventors"), "inventor_country"),
    }


def main():
    http = session({"X-Api-Key": require_env("PATENTSVIEW_API_KEY"), "Accept": "application/json"})
    end = date.today()
    start = end - timedelta(days=env_int("PATENTSVIEW_LOOKBACK_DAYS", 180))
    query = {"_and": [
        {"_gte": {"patent_date": start.isoformat()}},
        {"_lte": {"patent_date": end.isoformat()}},
        {"_or": [{"cpc_current.cpc_subclass_id": s} for s in CPC_SUBCLASSES]},
    ]}

    rows, after = [], None
    while True:
        opts = {"size": PAGE}
        if after:
            opts["after"] = after
        params = {
            "q": json.dumps(query), "f": json.dumps(FIELDS),
            "s": json.dumps([{"patent_id": "asc"}]), "o": json.dumps(opts),
        }
        r = http.get(URL, params=params, timeout=120)
        r.raise_for_status()
        batch = r.json().get("patents") or []
        rows.extend(flatten(p) for p in batch)
        print(f"[uspto] fetched {len(rows)}")
        if len(batch) < PAGE:
            break
        after = batch[-1]["patent_id"]
        time.sleep(1.5)  # API limit: 45 requests/minute

    upsert(pd.DataFrame(rows), "patents", "uspto", ["patent_id"], "patent_date", ext=".csv.gz")


if __name__ == "__main__":
    main()
