"""Temporary: check which free data endpoints answer from GitHub runners."""
import os

import requests

KEY = os.environ.get("EIA_API_KEY", "")
UA = {"User-Agent": "Mozilla/5.0 (research data collector)"}
EIA = "https://api.eia.gov/v2"

PROBES = {
    # EIA (same free key)
    "eia_respondents": f"{EIA}/electricity/rto/region-data/facet/respondent?api_key={KEY}",
    "eia_region_sample": f"{EIA}/electricity/rto/region-data/data/?api_key={KEY}&frequency=hourly&data[0]=value&length=3",
    "eia_interchange": f"{EIA}/electricity/rto/interchange-data/data/?api_key={KEY}&frequency=hourly&data[0]=value&length=3",
    "eia_subba": f"{EIA}/electricity/rto/region-sub-ba-data/data/?api_key={KEY}&frequency=hourly&data[0]=value&length=3",
    "eia_subba_facets": f"{EIA}/electricity/rto/region-sub-ba-data/facet/subba?api_key={KEY}",
    "eia_ng_price": f"{EIA}/natural-gas/pri/fut/data/?api_key={KEY}&frequency=daily&data[0]=value&length=3",
    "eia_petroleum_spot": f"{EIA}/petroleum/pri/spt/data/?api_key={KEY}&frequency=daily&data[0]=value&length=3",
    "eia_retail_sales": f"{EIA}/electricity/retail-sales/data/?api_key={KEY}&frequency=monthly&data[0]=price&length=3",
    # Europe / UK / Australia grids, keyless
    "energy_charts_power": "https://api.energy-charts.info/public_power?country=de&start=2026-09-20&end=2026-09-20T01:00",
    "energy_charts_price": "https://api.energy-charts.info/price?bzn=DE-LU&start=2026-09-20&end=2026-09-20T02:00",
    "energy_charts_load_fr": "https://api.energy-charts.info/public_power?country=fr&start=2015-01-05&end=2015-01-05T01:00",
    "uk_carbon_intensity": "https://api.carbonintensity.org.uk/intensity/date/2026-09-20",
    "uk_generation_mix": "https://api.carbonintensity.org.uk/generation/2026-09-20T00:00Z/2026-09-20T02:00Z",
    "elexon_demand": "https://data.elexon.co.uk/bmrs/api/v1/demand/outturn?settlementDateFrom=2026-09-20&settlementDateTo=2026-09-20&format=json",
    "elexon_fuelhh": "https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH?settlementDateFrom=2026-09-20&settlementDateTo=2026-09-20&format=json",
    "aemo_price_demand": "https://aemo.com.au/aemo/data/nem/priceanddemand/PRICE_AND_DEMAND_202608_NSW1.csv",
    "aemo_price_demand_old": "https://aemo.com.au/aemo/data/nem/priceanddemand/PRICE_AND_DEMAND_201501_NSW1.csv",
    # Macro / finance, keyless
    "fred_csv": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US,DGS10",
    # Real estate, keyless
    "redfin_metro": "https://redfin-public-data.s3.us-west-2.amazonaws.com/redfin_market_tracker/redfin_metro_market_tracker.tsv000.gz",
    "redfin_county": "https://redfin-public-data.s3.us-west-2.amazonaws.com/redfin_market_tracker/county_market_tracker.tsv000.gz",
    "realtor_metro": "https://econdata.s3-us-west-2.amazonaws.com/Reports/Core/RDC_Inventory_Core_Metrics_Metro_History.csv",
    "fhfa_hpi_new": "https://www.fhfa.gov/hpi/download/monthly/hpi_master.csv",
    "fhfa_hpi_old": "https://www.fhfa.gov/HPI_master.csv",
    "zillow_inventory": "https://files.zillowstatic.com/research/public_csvs/invt_fs/Metro_invt_fs_uc_sfrcondo_sm_month.csv",
    "zillow_sales_count": "https://files.zillowstatic.com/research/public_csvs/sales_count_now/Metro_sales_count_now_uc_sfrcondo_month.csv",
    "zillow_zhvi_zip": "https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
    "chotot_listing": "https://gateway.chotot.com/v1/public/ad-listing?cg=1000&region_v2=13000&limit=2",
    "batdongsan": "https://batdongsan.com.vn/ban-can-ho-chung-cu-tp-hcm",
    # Patents, keyless bulk tables
    "pv_bulk_patent": "https://s3.amazonaws.com/data.patentsview.org/download/g_patent.tsv.zip",
    "pv_bulk_cpc": "https://s3.amazonaws.com/data.patentsview.org/download/g_cpc_current.tsv.zip",
    "pv_bulk_abstract": "https://s3.amazonaws.com/data.patentsview.org/download/g_patent_abstract.tsv.zip",
    "pv_bulk_application": "https://s3.amazonaws.com/data.patentsview.org/download/g_application.tsv.zip",
    "pv_download_page": "https://patentsview.org/download/data-download-tables",
}


def main():
    for name, url in PROBES.items():
        shown = url.replace(KEY, "***") if KEY else url
        try:
            r = requests.get(url, headers=UA, timeout=60, stream=True)
            size = r.headers.get("Content-Length", "?")
            head = next(r.iter_content(400), b"")[:400]
            r.close()
            text = head.decode("utf-8", "replace").replace("\n", " | ")
            if KEY:
                text = text.replace(KEY, "***")
            print(f"### {name}: HTTP {r.status_code} len={size} type={r.headers.get('Content-Type', '?')}\n    {shown}\n    {text}")
        except Exception as e:
            print(f"### {name}: ERROR {type(e).__name__}: {e}\n    {shown}")


if __name__ == "__main__":
    main()
