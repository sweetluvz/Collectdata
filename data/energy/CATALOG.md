# Data catalog: `energy`

Auto-generated after every collection run by `scripts/build_catalog.py`.

| Table | Files | Rows | Time column | From | To | Size |
|---|---:|---:|---|---|---|---:|
| `energy/aemo/price_demand` | 113 | 177,151 | `timestamp` | 1998-12-06T16:00Z | 2026-09-27T14:00Z | 6.2 MB |
| `energy/airquality/observed` | 6 | 18,000 | `time` | 2022-08-04T00:00Z | 2026-09-27T17:00Z | 432.7 KB |
| `energy/eia/fuel_prices` | 489 | 129,990 | `period` | 1986-01-02 | 2026-09-22 | 1022.3 KB |
| `energy/eia/fuel_type` | 17 | 11,871 | `period` | 2018-07-01T05:00Z | 2026-09-27T06:00Z | 6.5 MB |
| `energy/eia/interchange` | 53 | 38,152 | `period` | 2015-07-01T05:00Z | 2026-09-26T07:00Z | 21.0 MB |
| `energy/eia/region` | 53 | 38,187 | `period` | 2015-07-01T05:00Z | 2026-09-27T18:00Z | 20.3 MB |
| `energy/eia/retail_sales` | 307 | 114,204 | `period` | 2001-01 | 2026-07 | 1.8 MB |
| `energy/eia/subregion` | 11 | 7,461 | `period` | 2019-01-01T00:00Z | 2026-09-27T07:00Z | 1.2 MB |
| `energy/europe/power` | 22 | 259,396 | `timestamp` | 2015-01-01T00:00Z | 2026-09-27T14:00Z | 11.2 MB |
| `energy/europe/price` | 13 | 9,239 | `timestamp` | 2015-01-01T00:00Z | 2026-09-28T21:45Z | 250.5 KB |
| `energy/gb/carbon_intensity` | 109 | 158,367 | `timestamp` | 2017-09-11T23:00Z | 2026-09-27T23:30Z | 1.0 MB |
| `energy/gb/demand` | 128 | 184,420 | `timestamp` | 2016-02-29T23:30Z | 2026-09-27T16:00Z | 1.6 MB |
| `energy/gb/generation` | 130 | 188,180 | `timestamp` | 2015-12-31T23:30Z | 2026-09-27T16:00Z | 5.3 MB |
| `energy/nyiso/lbmp_da` | 321 | 234,431 | `timestamp` | 2000-01-01T05:00Z | 2026-09-29T03:00Z | 8.5 MB |
| `energy/nyiso/lbmp_rt` | 141 | 102,445 | `timestamp` | 2015-01-01T05:00Z | 2026-09-27T17:00Z | 3.8 MB |
| `energy/weather/era5` | 141 | 4,110,720 | `time` | 2015-01-01T00:00Z | 2026-09-21T23:00Z | 103.3 MB |
| `energy/weather/forecast` | 1 | 4,898 | `issued_at` | 2026-09-27T08:00Z | 2026-09-27T17:00Z | 545.0 KB |
| `energy/weather/observed` | 1 | 3,600 | `time` | 2026-09-24T00:00Z | 2026-09-27T17:00Z | 336.6 KB |

## Backfill progress

| Source | Range | Chunks done | Skipped (no data) | Remaining |
|---|---|---:|---:|---:|
| `aemo` | 1998-12-01 .. 2026-09-27 | 110 / 334 | 0 | 224 |
| `airquality` | 2022-08-01 .. 2026-09-27 | 4 / 200 | 0 | 196 |
| `eia` | 2015-07-01 .. 2026-09-27 | 10 / 135 | 42 | 83 |
| `eia_bulk` | 2015-07-01 .. 2026-09-27 | 7 / 7 | 0 | complete |
| `eia_market` | 1986-01-01 .. 2026-09-27 | 41 / 41 | 0 | complete |
| `era5` | 2015-01-01 .. 2026-09-27 | 480 / 480 | 0 | complete |
| `europe_power` | 2015-01-01 .. 2026-09-27 | 204 / 1410 | 0 | 1206 |
| `europe_price` | 2015-01-01 .. 2026-09-27 | 12 / 141 | 0 | 129 |
| `gb` | 2016-01-01 .. 2026-09-27 | 129 / 129 | 0 | complete |
| `nyiso_da` | 2000-01-01 .. 2026-09-27 | 321 / 321 | 0 | complete |
| `nyiso_rt` | 2015-01-01 .. 2026-09-27 | 141 / 141 | 0 | complete |
