"""Chợ Tốt Nhà (nhatot.com / chotot.com) real-estate listings via the public JSON gateway - keyless.

Works from GitHub-hosted runners (unlike batdongsan.com.vn). Tables:
  realestate/chotot/ads       : one row per listing (latest state), partitioned by list_time month:
                                price, size, rooms, legal status, direction, coordinates, ward/street,
                                project, title and the start of the description
  realestate/chotot/snapshots : one row per (list_id, scraped_date) with the asking price, so price changes
                                and time on market can be reconstructed
Seller identity fields are never stored; phone numbers in text are masked. The gateway serves at most
10,000 results per query, so each (category, city) query is paged from the newest listing down.
"""
from datetime import datetime, timezone
import json
import random
import time

import pandas as pd

from utils.http import check, env_int, session
from utils.privacy import mask_phones
from utils.storage import upsert

URL = "https://gateway.chotot.com/v1/public/ad-listing"
CATEGORIES = {1010: "apartment", 1020: "house", 1040: "land"}
REGIONS = {13000: "hcm", 12000: "hanoi"}
PAGE = 50
MAX_OFFSET = 10000
FIELDS = [
    "list_id", "ad_id", "category", "type", "region_v2", "region_name", "area_v2", "area_name", "ward",
    "ward_name", "street_name", "pty_project_name", "latitude", "longitude", "price", "price_million_per_m2",
    "size", "living_size", "width", "length", "rooms", "toilets", "floors", "direction", "house_type",
    "apartment_type", "property_legal_document", "is_main_street", "furnishing_sell", "company_ad",
]


def flatten(ad, scraped_at, body_chars):
    row = {k: ad.get(k) for k in FIELDS}
    row["list_time"] = datetime.fromtimestamp(ad["list_time"] / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    row["scraped_at"] = scraped_at
    row["pty_characteristics"] = ";".join(str(x) for x in ad.get("pty_characteristics") or [])
    row["params"] = json.dumps({p.get("id"): p.get("value") for p in ad.get("params") or []}, ensure_ascii=False)
    row["subject"] = mask_phones(ad.get("subject"))
    row["body"] = mask_phones(ad.get("body"))[:body_chars] if body_chars else ""
    return row


def fetch_query(http, cg, region, max_pages):
    ads = []
    for page in range(max_pages):
        offset = page * PAGE
        if offset >= MAX_OFFSET:
            break
        r = check(http.get(URL, params={"cg": cg, "region_v2": region, "st": "s,k", "limit": PAGE, "o": offset},
                           timeout=60))
        batch = r.json().get("ads") or []
        ads.extend(batch)
        if len(batch) < PAGE:
            break
        time.sleep(random.uniform(1, 2))
    return ads


def main():
    http = session({"Accept": "application/json"})
    max_pages = env_int("CHOTOT_MAX_PAGES", 40)
    body_chars = env_int("CHOTOT_BODY_CHARS", 500)
    now = datetime.now(timezone.utc)
    scraped_at = now.strftime("%Y-%m-%dT%H:%MZ")

    rows, failures = {}, 0
    queries = [(cg, region) for cg in CATEGORIES for region in REGIONS]
    for cg, region in queries:
        try:
            ads = fetch_query(http, cg, region, max_pages)
        except Exception as e:
            failures += 1
            print(f"::warning::chotot cg={cg} region={region}: {e}")
            continue
        for ad in ads:
            if ad.get("list_id") and ad.get("list_time"):
                rows[ad["list_id"]] = flatten(ad, scraped_at, body_chars)
        print(f"[chotot] {CATEGORIES[cg]}/{REGIONS[region]}: {len(ads)} listings")
    if failures == len(queries):
        raise SystemExit("chotot: every query failed")

    if not rows:
        raise SystemExit("chotot: 0 listings returned - the gateway API may have changed")
    ads = pd.DataFrame(rows.values())
    upsert(ads, "realestate/chotot/ads", ["list_id"], "list_time")
    snaps = ads[["list_id", "price"]].assign(scraped_date=now.strftime("%Y-%m-%d"))
    upsert(snaps, "realestate/chotot/snapshots", ["list_id", "scraped_date"], "scraped_date")


if __name__ == "__main__":
    main()
