"""Lens.org Patent API - worldwide publications incl. WIPO (WO), EP, US, CN, with claims.

Token: https://www.lens.org/lens/user/subscriptions (Patent API access) -> secret LENS_API_TOKEN
Table: patents/lens/publications (partitioned by publication month). History: backfilled month by month.
Defaults to WO, EP and US publications (LENS_JURISDICTIONS) to keep weekly volume complete rather than
truncated. Stores first (independent) claim + claim count; LENS_FULL_CLAIMS=1 stores all claims
(roughly 10x larger files).
"""
from datetime import date, timedelta
import os
import time

import pandas as pd

from scrapers.patents.common import CPC_SUBCLASSES
from utils import backfill
from utils.http import check, env_int, require_env, session
from utils.storage import upsert

URL = "https://api.lens.org/patent/search"
EARLIEST = date(1900, 1, 1)
DEFAULT_START = date(2024, 1, 1)  # API quotas make long histories slow; widen via BACKFILL_START (see README)
FULL_CLAIMS = os.environ.get("LENS_FULL_CLAIMS") == "1"
JURISDICTIONS = [j.strip() for j in os.environ.get("LENS_JURISDICTIONS", "WO,EP,US").split(",") if j.strip()]
INCLUDE = [
    "lens_id", "jurisdiction", "doc_number", "kind", "date_published",
    "biblio.invention_title", "abstract", "claims",
    "biblio.classifications_cpc", "biblio.classifications_ipcr",
    "biblio.application_reference", "biblio.parties.applicants",
    "families.simple_family.size",
]


def pick_lang(items, key="text"):
    items = items or []
    for it in items:
        if it.get("lang") == "en":
            return it.get(key, "")
    return items[0].get(key, "") if items else ""


def claim_texts(claims):
    block = next((c for c in claims or [] if c.get("lang") == "en"), (claims or [None])[0])
    if not block:
        return []
    return [" ".join(c.get("claim_text") or []) for c in block.get("claims") or []]


def symbols(biblio, key):
    return ";".join(dict.fromkeys(c.get("symbol", "") for c in (biblio.get(key) or {}).get("classifications", [])))


def flatten(p, full_claims):
    b = p.get("biblio") or {}
    claims = claim_texts(p.get("claims"))
    applicants = (b.get("parties") or {}).get("applicants") or []
    return {
        "lens_id": p.get("lens_id"),
        "jurisdiction": p.get("jurisdiction"),
        "doc_number": p.get("doc_number"),
        "kind": p.get("kind"),
        "date_published": p.get("date_published"),
        "filing_date": (b.get("application_reference") or {}).get("date", ""),
        "title": pick_lang(b.get("invention_title")),
        "abstract": pick_lang(p.get("abstract")),
        "num_claims": len(claims),
        "first_claim": claims[0] if claims else "",
        "claims": "\n".join(claims) if full_claims else "",
        "cpc": symbols(b, "classifications_cpc"),
        "ipcr": symbols(b, "classifications_ipcr"),
        "applicants": ";".join(dict.fromkeys(
            (a.get("extracted_name") or {}).get("value", "") for a in applicants)),
        "applicant_countries": ";".join(dict.fromkeys(a.get("residence", "") for a in applicants if a.get("residence"))),
        "family_size": ((p.get("families") or {}).get("simple_family") or {}).get("size"),
    }


def collect(http, start, end, max_records):
    cpc_q = " OR ".join(f"{s}*" for s in CPC_SUBCLASSES)
    body = {
        "query": {"bool": {"must": [
            {"range": {"date_published": {"gte": start.isoformat(), "lte": end.isoformat()}}},
            {"query_string": {"query": f"class_cpc.symbol:({cpc_q})"}},
            {"terms": {"jurisdiction": JURISDICTIONS}},
        ]}},
        "size": 100,
        "scroll": "1m",
        "include": INCLUDE,
    }
    rows, total = [], 0
    while len(rows) < max_records:
        r = check(http.post(URL, json=body, timeout=120))
        res = r.json()
        total = res.get("total") or total
        batch = res.get("data") or []
        rows.extend(flatten(p, FULL_CLAIMS) for p in batch)
        print(f"[lens] {start}..{end}: fetched {len(rows)} / total {total}")
        if not batch or not res.get("scroll_id"):
            break
        body = {"scroll_id": res["scroll_id"], "scroll": "1m"}
        time.sleep(float(r.headers.get("x-rate-limit-retry-after-seconds", 0)) or 2)

    if total and len(rows) < int(total):
        print(f"::warning::lens: stored {len(rows)} of {total} matches - raise LENS_MAX_RECORDS or narrow the query")
    upsert(pd.DataFrame(rows), "patents/lens/publications", ["lens_id"], "date_published", gzip=True)
    return len(rows)


def main():
    backfill.register("patents", "lens", DEFAULT_START, EARLIEST)
    http = session(
        {"Authorization": f"Bearer {require_env('LENS_API_TOKEN')}", "Content-Type": "application/json"}, total=6
    )
    end = date.today()
    collect(http, end - timedelta(days=env_int("LENS_LOOKBACK_DAYS", 14)), end, env_int("LENS_MAX_RECORDS", 20000))

    def fetch_month(first, last):
        if not collect(http, first, last, 10**9):
            raise backfill.Skip("no publications in range")

    backfill.run("patents", "lens", DEFAULT_START, EARLIEST, backfill.month_chunks, fetch_month)

if __name__ == "__main__":
    main()
