"""Cleaned Chợ Tốt listing table for hedonic analysis, with an explicit drop-reason log.

Asking prices, not transaction prices; see README section 11 before using them as house values.
"""
import numpy as np
import pandas as pd

from processing.io import output_dir
from utils.storage import load_all

CITY = {13000: "hcm", 12000: "hanoi"}
CATEGORY = {1010: "apartment", 1020: "house", 1040: "land"}
PPM2_BOUNDS = (1e6, 1e9)   # VND per m2: below 1 million or above 1 billion is treated as a data-entry error
MAD_K = 4.0


def clean_chotot():
    ads = load_all("realestate/chotot/ads")
    if ads.empty:
        return None, {}
    ads = ads.sort_values("list_time").drop_duplicates("list_id", keep="last")
    num = ["price", "size", "living_size", "rooms", "toilets", "floors", "latitude", "longitude", "width", "length"]
    for c in num:
        if c in ads:
            ads[c] = pd.to_numeric(ads[c], errors="coerce")
    ads["city"] = pd.to_numeric(ads["region_v2"], errors="coerce").map(CITY)
    ads["category_name"] = pd.to_numeric(ads["category"], errors="coerce").map(CATEGORY)
    ads["price_per_m2"] = ads["price"] / ads["size"]

    reasons = pd.Series("", index=ads.index)

    def drop(mask, why):
        reasons[mask & (reasons == "")] = why

    drop(ads.get("type", pd.Series("s", index=ads.index)).ne("s"), "not_for_sale")
    drop(ads["price"].isna() | (ads["price"] <= 0), "no_price")
    drop(ads["size"].isna() | (ads["size"] <= 0), "no_size")
    drop(~ads["price_per_m2"].between(*PPM2_BOUNDS), "price_per_m2_implausible")
    drop(ads["latitude"].isna() | ads["longitude"].isna(), "no_coordinates")

    # robust outliers of log price per m2 within each (city, category)
    logp = np.log(ads["price_per_m2"].where(reasons == ""))
    grp = logp.groupby([ads["city"], ads["category_name"]])
    med = grp.transform("median")
    mad = grp.transform(lambda x: (x - x.median()).abs().median() * 1.4826)
    drop((logp - med).abs() > MAD_K * mad, "price_per_m2_outlier")

    snaps = load_all("realestate/chotot/snapshots")
    if not snaps.empty:
        seen = snaps.groupby("list_id")["scraped_date"].agg(first_seen="min", last_seen="max", days_seen="nunique")
        ads = ads.merge(seen, left_on="list_id", right_index=True, how="left")

    ads["drop_reason"] = reasons.reindex(ads.index).values
    kept = ads[ads["drop_reason"] == ""].drop(columns="drop_reason")
    path = output_dir() / "chotot" / "ads_clean.csv.gz"
    path.parent.mkdir(parents=True, exist_ok=True)
    kept.to_csv(path, index=False, compression={"method": "gzip", "mtime": 0})
    summary = {"listings": len(ads), "kept": len(kept),
               **ads.loc[ads["drop_reason"] != "", "drop_reason"].value_counts().to_dict()}
    print(f"[chotot] {summary} -> {path}")
    return path, summary
