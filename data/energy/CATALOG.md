# Data catalog: `energy`

Auto-generated after every collection run by `scripts/build_catalog.py`.

| Table | Files | Rows | Time column | From | To | Size |
|---|---:|---:|---|---|---|---:|
| `energy/aemo/price_demand` | 334 | 925,327 | `timestamp` | 1998-12-06T16:00Z | 2026-09-28T14:00Z | 29.6 MB |
| `energy/airquality/observed` | 50 | 1,457,384 | `time` | 2022-08-01T00:00Z | 2026-09-29T04:00Z | 24.0 MB |
| `energy/eia/fuel_prices` | 489 | 129,990 | `period` | 1986-01-02 | 2026-09-22 | 1022.3 KB |
| `energy/eia/fuel_type` | 96 | 69,591 | `period` | 2018-07-01T05:00Z | 2026-09-28T06:00Z | 41.3 MB |
| `energy/eia/interchange` | 132 | 95,872 | `period` | 2015-07-01T05:00Z | 2026-09-27T07:00Z | 55.9 MB |
| `energy/eia/region` | 132 | 95,917 | `period` | 2015-07-01T05:00Z | 2026-09-29T04:00Z | 54.9 MB |
| `energy/eia/retail_sales` | 307 | 114,204 | `period` | 2001-01 | 2026-07 | 1.8 MB |
| `energy/eia/subregion` | 90 | 65,181 | `period` | 2019-01-01T00:00Z | 2026-09-28T07:00Z | 10.9 MB |
| `energy/europe/power` | 141 | 2,132,424 | `timestamp` | 2015-01-01T00:00Z | 2026-09-29T05:15Z | 96.3 MB |
| `energy/europe/price` | 141 | 129,166 | `timestamp` | 2015-01-01T00:00Z | 2026-09-29T21:45Z | 4.4 MB |
| `energy/gb/carbon_intensity` | 109 | 158,463 | `timestamp` | 2017-09-11T23:00Z | 2026-09-29T23:30Z | 1.0 MB |
| `energy/gb/demand` | 128 | 184,496 | `timestamp` | 2016-02-29T23:30Z | 2026-09-29T06:00Z | 1.6 MB |
| `energy/gb/generation` | 130 | 188,256 | `timestamp` | 2015-12-31T23:30Z | 2026-09-29T06:00Z | 5.3 MB |
| `energy/nyiso/lbmp_da` | 321 | 234,455 | `timestamp` | 2000-01-01T05:00Z | 2026-09-30T03:00Z | 8.5 MB |
| `energy/nyiso/lbmp_rt` | 321 | 233,976 | `timestamp` | 2000-01-01T05:00Z | 2026-09-29T04:00Z | 8.7 MB |
| `energy/weather/era5` | 141 | 4,112,640 | `time` | 2015-01-01T00:00Z | 2026-09-23T23:00Z | 103.5 MB |
| `energy/weather/forecast` | 1 | 25,058 | `issued_at` | 2026-09-27T08:00Z | 2026-09-29T04:00Z | 2.7 MB |
| `energy/weather/observed` | 1 | 5,000 | `time` | 2026-09-24T00:00Z | 2026-09-29T04:00Z | 467.3 KB |

## Backfill progress

| Source | Range | Chunks done | Skipped (no data) | Remaining |
|---|---|---:|---:|---:|
| `aemo` | 1998-12-01 .. 2026-09-27 | 334 / 334 | 0 | complete |
| `airquality` | 2022-08-01 .. 2026-09-27 | 200 / 200 | 0 | complete |
| `eia` | 2015-07-01 .. 2026-09-27 | 89 / 135 | 42 | 4 |
| `eia_bulk` | 2015-07-01 .. 2026-09-27 | 7 / 7 | 0 | complete |
| `eia_market` | 1986-01-01 .. 2026-09-27 | 41 / 41 | 0 | complete |
| `era5` | 2015-01-01 .. 2026-09-27 | 480 / 480 | 0 | complete |
| `europe_power` | 2015-01-01 .. 2026-09-27 | 1410 / 1410 | 0 | complete |
| `europe_price` | 2015-01-01 .. 2026-09-27 | 141 / 141 | 0 | complete |
| `gb` | 2016-01-01 .. 2026-09-27 | 129 / 129 | 0 | complete |
| `nyiso_da` | 2000-01-01 .. 2026-09-27 | 321 / 321 | 0 | complete |
| `nyiso_rt` | 2000-01-01 .. 2026-09-27 | 321 / 321 | 0 | complete |
