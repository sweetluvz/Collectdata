"""Lens.org Patent API - worldwide publications incl. WIPO (WO), EP, US, CN, with claims.

Token: https://www.lens.org/lens/user/subscriptions (Patent API access) -> secret LENS_API_TOKEN
Stores first (independent) claim + claim count by default; set LENS_FULL_CLAIMS=1 to store all claims
(roughly 10x larger files).
"""
from datetime import date, timedelta
import os
import time

import pandas as pd

from scrapers.patents.common import CPC_SUBCLASSES
from utils.http import env_int, require_env, session
from utils.storage import upsert

URL = "https://api.lens.org/patent/search"
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


def main():
    http = session({"Authorization": f"Bearer {require_env('LENS_API_TOKEN')}", "Content-Type": "application/json"})
    full_claims = os.environ.get("LENS_FULL_CLAIMS") == "1"
    max_records = env_int("LENS_MAX_RECORDS", 5000)
    end = date.today()
    start = end - timedelta(days=env_int("LENS_LOOKBACK_DAYS", 14))
    cpc_q = " OR ".join(f"{s}*" for s in CPC_SUBCLASSES)
    body = {
        "query": {"bool": {"must": [
            {"range": {"date_published": {"gte": start.isoformat(), "lte": end.isoformat()}}},
            {"query_string": {"query": f"class_cpc.symbol:({cpc_q})"}},
        ]}},
        "size": 100,
        "scroll": "1m",
        "include": INCLUDE,
    }

    rows = []
    while len(rows) < max_records:
        r = http.post(URL, json=body, timeout=120)
        r.raise_for_status()
        res = r.json()
        batch = res.get("data") or []
        rows.extend(flatten(p, full_claims) for p in batch)
        print(f"[lens] fetched {len(rows)} / total {res.get('total')}")
        if not batch or not res.get("scroll_id"):
            break
        body = {"scroll_id": res["scroll_id"], "scroll": "1m"}
        time.sleep(float(r.headers.get("x-rate-limit-retry-after-seconds", 0)) or 2)

    upsert(pd.DataFrame(rows), "patents", "lens", ["lens_id"], "date_published", ext=".csv.gz")


if __name__ == "__main__":
    main()
