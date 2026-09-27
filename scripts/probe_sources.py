"""Temporary: check which free data endpoints answer from GitHub runners (round 2)."""
import json
import os

import requests

KEY = os.environ.get("EIA_API_KEY", "")
UA = {"User-Agent": "Mozilla/5.0 (research data collector)"}
EIA = "https://api.eia.gov/v2"

PROBES = {
    "energy_charts_nodates": "https://api.energy-charts.info/public_power?country=de",
    "energy_charts_iso": "https://api.energy-charts.info/public_power?country=de&start=2026-09-20T00:00%2B00:00&end=2026-09-20T02:00%2B00:00",
    "energy_charts_date": "https://api.energy-charts.info/public_power?country=fr&start=2026-09-20&end=2026-09-21",
    "energy_charts_price": "https://api.energy-charts.info/price?bzn=DE-LU&start=2026-09-20&end=2026-09-21",
    "energy_charts_total": "https://api.energy-charts.info/total_power?country=de&start=2026-09-20&end=2026-09-21",
    "energy_charts_old": "https://api.energy-charts.info/public_power?country=de&start=2015-01-05&end=2015-01-06",
    "fred_single": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US",
    "nyiso_da_zip": "http://mis.nyiso.com/public/csv/damlbmp/20260801damlbmp_zone_csv.zip",
    "nyiso_da_day": "http://mis.nyiso.com/public/csv/damlbmp/20260920damlbmp_zone.csv",
    "nyiso_da_old": "http://mis.nyiso.com/public/csv/damlbmp/20150101damlbmp_zone_csv.zip",
    "nyiso_rt_zip": "http://mis.nyiso.com/public/csv/rtlbmp/20260801rtlbmp_zone_csv.zip",
    "elexon_demand_2016": "https://data.elexon.co.uk/bmrs/api/v1/demand/outturn?settlementDateFrom=2016-01-01&settlementDateTo=2016-01-01&format=json",
    "elexon_fuelhh_2016": "https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH?settlementDateFrom=2016-01-01&settlementDateTo=2016-01-01&format=json",
    "elexon_fuelhh_range": "https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH?settlementDateFrom=2026-08-01&settlementDateTo=2026-08-31&format=json",
    "uk_carbon_2018": "https://api.carbonintensity.org.uk/intensity/2018-01-01T00:00Z/2018-01-14T00:00Z",
    "aemo_1999": "https://aemo.com.au/aemo/data/nem/priceanddemand/PRICE_AND_DEMAND_199901_NSW1.csv",
    "aemo_tas": "https://aemo.com.au/aemo/data/nem/priceanddemand/PRICE_AND_DEMAND_202608_TAS1.csv",
    "fhfa_quarterly_len": "https://www.fhfa.gov/hpi/download/quarterly_datasets/hpi_at_bdl_cbsa.csv",
    "realtor_county": "https://econdata.s3-us-west-2.amazonaws.com/Reports/Core/RDC_Inventory_Core_Metrics_County_History.csv",
    "zillow_days_pending": "https://files.zillowstatic.com/research/public_csvs/mean_doz_pending/Metro_mean_doz_pending_uc_sfrcondo_sm_month.csv",
    "zillow_new_listings": "https://files.zillowstatic.com/research/public_csvs/new_listings/Metro_new_listings_uc_sfrcondo_sm_month.csv",
    "zillow_price_cut": "https://files.zillowstatic.com/research/public_csvs/perc_listings_price_cut/Metro_perc_listings_price_cut_uc_sfrcondo_sm_month.csv",
    "zillow_zhvf": "https://files.zillowstatic.com/research/public_csvs/zhvf_growth/Metro_zhvf_growth_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
}

JSON_PROBES = {
    "chotot_hcm_house": "https://gateway.chotot.com/v1/public/ad-listing?cg=1020&region_v2=13000&st=s,k&limit=50&o=0",
    "chotot_hn_apartment": "https://gateway.chotot.com/v1/public/ad-listing?cg=1010&region_v2=12000&st=s,k&limit=50&o=5000",
    "chotot_deep_offset": "https://gateway.chotot.com/v1/public/ad-listing?cg=1000&limit=50&o=20000",
    "eia_price_row": f"{EIA}/petroleum/pri/spt/data/?api_key={KEY}&frequency=daily&data[0]=value&length=1&facets[series][]=RWTC",
    "eia_ng_row": f"{EIA}/natural-gas/pri/fut/data/?api_key={KEY}&frequency=daily&data[0]=value&length=1&facets[series][]=RNGWHHD",
    "eia_subba_row": f"{EIA}/electricity/rto/region-sub-ba-data/data/?api_key={KEY}&frequency=hourly&data[0]=value&length=1",
    "eia_interchange_row": f"{EIA}/electricity/rto/interchange-data/data/?api_key={KEY}&frequency=hourly&data[0]=value&length=1",
    "eia_region_2015": f"{EIA}/electricity/rto/region-data/data/?api_key={KEY}&frequency=hourly&data[0]=value&length=1&start=2015-07-01T00&end=2015-07-01T05",
}


def show(name, url, r, body):
    shown = url.replace(KEY, "***") if KEY else url
    body = body.replace(KEY, "***") if KEY else body
    print(f"### {name}: HTTP {r.status_code} len={r.headers.get('Content-Length', '?')} "
          f"type={r.headers.get('Content-Type', '?')}\n    {shown}\n    {body}")


def main():
    for name, url in PROBES.items():
        try:
            r = requests.get(url, headers=UA, timeout=90, stream=True)
            head = next(r.iter_content(500), b"")[:500]
            r.close()
            show(name, url, r, head.decode("utf-8", "replace").replace("\n", " | "))
        except Exception as e:
            print(f"### {name}: ERROR {type(e).__name__}: {e}")
    for name, url in JSON_PROBES.items():
        try:
            r = requests.get(url, headers=UA, timeout=90)
            data = r.json()
            if "ads" in data:
                ads = data["ads"]
                ad = ads[0] if ads else {}
                personal = ("account", "phone", "avatar", "name", "seller", "body", "subject", "image", "webp")
                sample = {k: v for k, v in ad.items() if not any(p in k for p in personal)}
                body = f"total={data.get('total')} n={len(ads)} keys={sorted(ad)}\n    sample={json.dumps(sample, ensure_ascii=False)[:1500]}"
            else:
                body = json.dumps(data, ensure_ascii=False)[:1200]
            show(name, url, r, body)
        except Exception as e:
            print(f"### {name}: ERROR {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
