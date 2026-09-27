from unittest import mock

import pytest

from conftest import FakeResponse
from utils.storage import load_all

CARD = """
<div class="js__card" prid="41234567">
  <a class="js__product-link-for-product-id" href="/ban-can-ho-chung-cu-quan-7/abc-pr41234567">
    <h3 class="re__card-title"><span class="pr-title">Căn hộ 2PN Q7</span></h3></a>
  <span class="re__card-config-price">3,5 tỷ</span><span class="re__card-config-area">70 m²</span>
  <span class="re__card-config-bedroom">2</span><div class="re__card-location">Quận 7, Hồ Chí Minh</div>
</div>
<div class="js__card"><a href="/ban-nha/x-pr999"><h3>Nhà</h3></a><span class="re__card-config-price">Thỏa thuận</span></div>
"""
DETAIL = """
<div class="re__pr-short-description">Đường Nguyễn Lương Bằng, Quận 7</div>
<div class="re__section-body re__detail-content">Căn hộ view sông.</div>
<div class="re__pr-specs-content-item"><span class="re__pr-specs-content-item-title">Pháp lý</span>
  <span class="re__pr-specs-content-item-value">Sổ hồng</span></div>
<div class="re__pr-short-info-item"><span class="title">Ngày đăng</span><span class="value">25/09/2026</span></div>
<iframe data-src="https://www.google.com/maps/embed/v1/place?q=10.7291,106.7189&key=x"></iframe>
"""
BLOCK = FakeResponse(text="<title>Just a moment...</title>", status=403)


@pytest.mark.parametrize("text,area,expected", [
    ("3,5 tỷ", 70, 3.5e9),
    ("850 triệu", None, 8.5e8),
    ("25 triệu/m²", 80, 2.0e9),
    ("25 triệu/m²", None, None),
    ("Thỏa thuận", 50, None),
])
def test_parse_price(text, area, expected):
    from scrapers.realestate.batdongsan_collector import parse_price_vnd

    assert parse_price_vnd(text, area) == expected


def run_bds(get):
    import scrapers.realestate.batdongsan_collector as bd

    with mock.patch.object(bd, "SEARCHES", bd.SEARCHES[:2]), mock.patch.object(bd, "pause"), \
         mock.patch("requests.Session.get", side_effect=get):
        bd.main()


def test_batdongsan_listings_and_details(data_dir):
    def get(url, timeout=None):
        if "-pr" in url:
            return FakeResponse(text=DETAIL)
        return FakeResponse(text="<html></html>" if "/p2" in url else CARD)

    run_bds(get)
    listings = load_all("realestate/batdongsan/listings")
    assert set(listings.listing_id) == {"41234567", "999"}
    row = listings[listings.listing_id == "41234567"].iloc[0]
    assert (row.price_vnd, row.area_m2, row.bedrooms) == ("3500000000.0", "70.0", "2.0")
    details = load_all("realestate/batdongsan/details")
    assert details.iloc[0][["latitude", "longitude"]].tolist() == ["10.7291", "106.7189"]
    assert "Sổ hồng" in details.iloc[0].specs_json


def test_batdongsan_saves_partial_data_when_blocked(data_dir):
    def get(url, timeout=None):
        return FakeResponse(text=CARD) if url.endswith("tp-hcm") and "nha-rieng" not in url else BLOCK

    with pytest.raises(SystemExit, match="blocked"):
        run_bds(get)
    assert len(load_all("realestate/batdongsan/listings")) == 2
    assert load_all("realestate/batdongsan/details").empty


def test_zillow_stores_each_release_once(data_dir):
    import scrapers.realestate.zillow_collector as zc

    csv = b"RegionID,RegionName,2026-07-31,2026-08-31\n1,US,350000,351000\n"
    with mock.patch("requests.Session.get", return_value=FakeResponse(content=csv)):
        zc.main()
        zc.main()
    files = sorted(p.relative_to(data_dir).as_posix() for p in data_dir.rglob("*.gz"))
    assert files == [f"realestate/zillow/{n}/2026-08.csv.gz" for n in sorted(zc.DATASETS)]


def test_phone_numbers_are_masked():
    from scrapers.realestate.batdongsan_collector import mask_phones

    text = "Liên hệ 0912 345 678 hoặc +84 912.345.678, giá 3,5 tỷ, 70 m2, năm 2024"
    assert mask_phones(text) == "Liên hệ [SĐT] hoặc [SĐT], giá 3,5 tỷ, 70 m2, năm 2024"
