# Data catalog: `energy`

Auto-generated after every collection run by `scripts/build_catalog.py`.

| Table | Files | Rows | Time column | From | To | Size |
|---|---:|---:|---|---|---|---:|
| `energy/aemo/price_demand` | 335 | 927,919 | `timestamp` | 1998-12-06T16:00Z | 2026-10-07T14:00Z | 29.3 MB |
| `energy/airquality/observed` | 51 | 1,466,784 | `time` | 2022-08-01T00:00Z | 2026-10-08T23:00Z | 23.2 MB |
| `energy/eia/fuel_prices` | 490 | 130,110 | `period` | 1986-01-02 | 2026-10-06 | 1007.4 KB |
| `energy/eia/fuel_type` | 100 | 72,506 | `period` | 2018-07-01T05:00Z | 2026-10-08T06:00Z | 46.1 MB |
| `energy/eia/interchange` | 136 | 98,787 | `period` | 2015-07-01T05:00Z | 2026-10-07T07:00Z | 59.6 MB |
| `energy/eia/region` | 136 | 98,827 | `period` | 2015-07-01T05:00Z | 2026-10-08T23:00Z | 58.6 MB |
| `energy/eia/retail_sales` | 307 | 114,204 | `period` | 2001-01 | 2026-07 | 1.8 MB |
| `energy/eia/subregion` | 94 | 68,096 | `period` | 2019-01-01T00:00Z | 2026-10-08T07:00Z | 12.0 MB |
| `energy/europe/power` | 142 | 2,139,988 | `timestamp` | 2015-01-01T00:00Z | 2026-10-08T12:00Z | 95.1 MB |
| `energy/europe/price` | 142 | 130,126 | `timestamp` | 2015-01-01T00:00Z | 2026-10-09T21:45Z | 4.3 MB |
| `energy/gb/carbon_intensity` | 110 | 158,895 | `timestamp` | 2017-09-11T23:00Z | 2026-10-08T23:30Z | 1008.0 KB |
| `energy/gb/demand` | 129 | 184,942 | `timestamp` | 2016-02-29T23:30Z | 2026-10-08T13:00Z | 1.6 MB |
| `energy/gb/generation` | 131 | 188,702 | `timestamp` | 2015-12-31T23:30Z | 2026-10-08T13:00Z | 5.3 MB |
| `energy/nyiso/lbmp_da` | 322 | 234,695 | `timestamp` | 2000-01-01T05:00Z | 2026-10-10T03:00Z | 8.5 MB |
| `energy/nyiso/lbmp_rt` | 322 | 234,201 | `timestamp` | 2000-01-01T05:00Z | 2026-10-08T13:00Z | 8.7 MB |
| `energy/weather/era5` | 142 | 4,121,280 | `time` | 2015-01-01T00:00Z | 2026-10-02T23:00Z | 102.2 MB |
| `energy/weather/forecast` | 2 | 66,338 | `issued_at` | 2026-09-27T08:00Z | 2026-10-08T23:00Z | 7.2 MB |
| `energy/weather/observed` | 2 | 14,400 | `time` | 2026-09-24T00:00Z | 2026-10-08T23:00Z | 1.3 MB |

## Backfill progress

| Source | Range | Chunks done | Skipped (no data) | Remaining |
|---|---|---:|---:|---:|
| `aemo` | 1998-12-01 .. 2026-09-27 | 334 / 334 | 0 | complete |
| `airquality` | 2022-08-01 .. 2026-09-27 | 200 / 200 | 0 | complete |
| `eia` | 2015-07-01 .. 2026-09-27 | 93 / 135 | 42 | complete |
| `eia_bulk` | 2015-07-01 .. 2026-09-27 | 7 / 7 | 0 | complete |
| `eia_market` | 1986-01-01 .. 2026-09-27 | 41 / 41 | 0 | complete |
| `era5` | 2015-01-01 .. 2026-09-27 | 480 / 480 | 0 | complete |
| `europe_power` | 2015-01-01 .. 2026-09-27 | 1410 / 1410 | 0 | complete |
| `europe_price` | 2015-01-01 .. 2026-09-27 | 141 / 141 | 0 | complete |
| `gb` | 2016-01-01 .. 2026-09-27 | 129 / 129 | 0 | complete |
| `nyiso_da` | 2000-01-01 .. 2026-09-27 | 321 / 321 | 0 | complete |
| `nyiso_rt` | 2000-01-01 .. 2026-09-27 | 321 / 321 | 0 | complete |
