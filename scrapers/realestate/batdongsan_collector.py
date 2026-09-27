"""batdongsan.com.vn listing scraper.

Tables:
  realestate/batdongsan/listings : one row per (listing_id, scraped_date) -> daily panel of asking prices
  realestate/batdongsan/details  : one row per listing_id, fetched once -> coordinates, description, specs

CSS selectors reflect the site's markup at time of writing; if a run parses 0 cards the job fails
loudly so the selectors can be updated. If the site starts blocking mid-run, everything collected so far
is still saved and the job is then marked failed. Requests are spaced a few seconds apart.
"""
from datetime import datetime, timezone
import json
import random
import re
import time

import pandas as pd
from bs4 import BeautifulSoup

from utils.http import check, env_int, session
from utils.privacy import mask_phones
from utils.storage import load_all, upsert

BASE = "https://batdongsan.com.vn"
SEARCHES = [
    ("ban-can-ho-chung-cu-tp-hcm", "apartment_sale", "hcm"),
    ("ban-nha-rieng-tp-hcm", "house_sale", "hcm"),
    ("ban-can-ho-chung-cu-ha-noi", "apartment_sale", "hanoi"),
    ("ban-nha-rieng-ha-noi", "house_sale", "hanoi"),
    ("ban-can-ho-chung-cu-da-nang", "apartment_sale", "danang"),
    ("ban-dat-tp-hcm", "land_sale", "hcm"),
]
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
    "Referer": BASE + "/",
}
BLOCK_MARKERS = ("Just a moment", "cf-browser-verification", "Attention Required", "captcha")


class Blocked(RuntimeError):
    pass


def pause():
    time.sleep(random.uniform(3, 6))


def get_html(http, url):
    r = http.get(url, timeout=45)
    if r.status_code in (403, 429, 503) or any(m in r.text[:5000] for m in BLOCK_MARKERS):
        raise Blocked(f"{url} -> HTTP {r.status_code} (anti-bot page)")
    return check(r).text


def first_text(node, *selectors):
    for sel in selectors:
        el = node.select_one(sel)
        if el and el.get_text(strip=True):
            return el.get_text(" ", strip=True)
    return ""


def parse_number(text):
    m = re.search(r"\d+(?:[.,]\d+)?", text.replace(" ", ""))
    return float(m.group().replace(",", ".")) if m else None


def parse_area(text):
    return parse_number(text) if "m" in text else None


def parse_price_vnd(text, area):
    """'3,5 tỷ' -> 3.5e9, '850 triệu' -> 8.5e8, '25 triệu/m²' -> 25e6*area; 'Thỏa thuận' -> None."""
    t = text.lower()
    value = parse_number(t)
    if value is None:
        return None
    if "tỷ" in t:
        value *= 1e9
    elif "triệu" in t:
        value *= 1e6
    elif "nghìn" in t or "ngàn" in t:
        value *= 1e3
    if "/m" in t:
        return value * area if area else None
    return value


def listing_id(card, url):
    for attr in ("prid", "data-product-id", "data-prid"):
        el = card if card.has_attr(attr) else card.select_one(f"[{attr}]")
        if el is not None and el.get(attr):
            return str(el.get(attr))
    m = re.search(r"-pr(\d+)", url or "")
    return m.group(1) if m else ""


def parse_cards(html, category, city, scraped_at):
    soup = BeautifulSoup(html, "lxml")
    cards = soup.select("div.js__card") or soup.select("div.re__card-full") or soup.select("div[class*='re__card']")
    rows = []
    for c in cards:
        link = c.select_one("a.js__product-link-for-product-id") or c.select_one("a[href*='-pr']")
        url = link["href"] if link and link.has_attr("href") else ""
        if url.startswith("/"):
            url = BASE + url
        lid = listing_id(c, url)
        if not lid:
            continue
        area_txt = first_text(c, ".re__card-config-area", "span[class*='area']")
        price_txt = first_text(c, ".re__card-config-price", "span[class*='price']")
        area = parse_area(area_txt)
        rows.append({
            "listing_id": lid,
            "scraped_date": scraped_at[:10],
            "scraped_at": scraped_at,
            "category": category,
            "city": city,
            "title": mask_phones(first_text(c, ".re__card-title", ".pr-title", "h3")),
            "price_text": price_txt,
            "price_vnd": parse_price_vnd(price_txt, area),
            "area_m2": area,
            "price_per_m2_text": first_text(c, ".re__card-config-price_per_m2"),
            "bedrooms": parse_number(first_text(c, ".re__card-config-bedroom")),
            "toilets": parse_number(first_text(c, ".re__card-config-toilet")),
            "location": first_text(c, ".re__card-location", "div[class*='location']"),
            "published_text": first_text(c, ".re__card-published-info-published-at"),
            "is_vip": bool(c.select_one("[class*='vip']")),
            "url": url,
        })
    return rows, len(cards)


def parse_detail(html, lid, scraped_at):
    soup = BeautifulSoup(html, "lxml")
    specs = {}
    for item in soup.select(".re__pr-specs-content-item"):
        k = first_text(item, ".re__pr-specs-content-item-title")
        v = first_text(item, ".re__pr-specs-content-item-value")
        if k:
            specs[k] = v
    short = {}
    for item in soup.select(".re__pr-short-info-item"):
        k = first_text(item, ".title")
        v = first_text(item, ".value")
        if k:
            short[k] = v
    lat = lon = None
    for el in soup.select("iframe[data-src], iframe[src]"):
        m = re.search(r"q=(-?\d+\.\d+),\s*(-?\d+\.\d+)", el.get("data-src") or el.get("src") or "")
        if m:
            lat, lon = float(m.group(1)), float(m.group(2))
            break
    return {
        "listing_id": lid,
        "fetched_at": scraped_at,
        "latitude": lat,
        "longitude": lon,
        "address": first_text(soup, ".re__pr-short-description", ".js__pr-address"),
        "description": mask_phones(first_text(soup, ".re__detail-content", ".re__section-body.re__detail-content")),
        "posted_date": short.get("Ngày đăng", ""),
        "expiry_date": short.get("Ngày hết hạn", ""),
        "listing_type": short.get("Loại tin", ""),
        "specs_json": json.dumps(specs, ensure_ascii=False),
    }


def main():
    http = session(HEADERS, total=2)
    max_pages = env_int("BDS_MAX_PAGES", 5)
    detail_limit = env_int("BDS_DETAIL_LIMIT", 80)
    scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")

    rows = []
    blocked = None
    for slug, category, city in SEARCHES:
        if blocked:
            break
        for page in range(1, max_pages + 1):
            url = f"{BASE}/{slug}" + (f"/p{page}" if page > 1 else "")
            try:
                html = get_html(http, url)
            except Blocked as e:
                blocked = e
                break
            except Exception as e:
                print(f"::warning::batdongsan {url}: {e}")
                break
            parsed, n_cards = parse_cards(html, category, city, scraped_at)
            print(f"[batdongsan] {url}: {n_cards} cards, {len(parsed)} parsed")
            rows.extend(parsed)
            pause()
            if not parsed:
                break

    if not rows:
        raise SystemExit(f"batdongsan: 0 listings parsed - {blocked or 'markup probably changed, update selectors'}")
    listings = pd.DataFrame(rows).drop_duplicates(["listing_id", "scraped_date"], keep="last")
    upsert(listings, "realestate/batdongsan/listings", ["listing_id", "scraped_date"], "scraped_at")

    known = load_all("realestate/batdongsan/details")
    seen = set(known["listing_id"]) if not known.empty else set()
    todo = listings[~listings["listing_id"].isin(seen)].head(0 if blocked else detail_limit)
    details = []
    for lid, url in zip(todo["listing_id"], todo["url"]):
        try:
            details.append(parse_detail(get_html(http, url), lid, scraped_at))
        except Blocked as e:
            blocked = e
            break
        except Exception as e:
            print(f"::warning::batdongsan detail {lid}: {e}")
        pause()
    upsert(pd.DataFrame(details), "realestate/batdongsan/details", ["listing_id"], "fetched_at")

    if blocked:
        raise SystemExit(f"batdongsan: blocked by anti-bot protection ({blocked}); partial data saved")

if __name__ == "__main__":
    main()
