# Data catalog: `energy`

Auto-generated after every collection run by `scripts/build_catalog.py`.

| Table | Files | Rows | Time column | From | To | Size |
|---|---:|---:|---|---|---|---:|
| `energy/aemo/price_demand` | 334 | 925,327 | `timestamp` | 1998-12-06T16:00Z | 2026-09-28T14:00Z | 29.6 MB |
| `energy/airquality/observed` | 50 | 1,456,944 | `time` | 2022-08-01T00:00Z | 2026-09-28T17:00Z | 24.0 MB |
| `energy/eia/fuel_prices` | 489 | 129,990 | `period` | 1986-01-02 | 2026-09-22 | 1022.3 KB |
| `energy/eia/fuel_type` | 51 | 36,735 | `period` | 2018-07-01T05:00Z | 2026-09-28T06:00Z | 21.0 MB |
| `energy/eia/interchange` | 86 | 62,272 | `period` | 2015-07-01T05:00Z | 2026-09-27T07:00Z | 35.8 MB |
| `energy/eia/region` | 87 | 63,050 | `period` | 2015-07-01T05:00Z | 2026-09-28T17:00Z | 35.4 MB |
| `energy/eia/retail_sales` | 307 | 114,204 | `period` | 2001-01 | 2026-07 | 1.8 MB |
| `energy/eia/subregion` | 44 | 31,581 | `period` | 2019-01-01T00:00Z | 2026-09-28T07:00Z | 5.2 MB |
| `energy/europe/power` | 140 | 2,065,596 | `timestamp` | 2015-01-01T00:00Z | 2026-09-28T16:30Z | 87.7 MB |
| `energy/europe/price` | 141 | 129,166 | `timestamp` | 2015-01-01T00:00Z | 2026-09-29T21:45Z | 4.4 MB |
| `energy/gb/carbon_intensity` | 109 | 158,415 | `timestamp` | 2017-09-11T23:00Z | 2026-09-28T23:30Z | 1.0 MB |
| `energy/gb/demand` | 128 | 184,470 | `timestamp` | 2016-02-29T23:30Z | 2026-09-28T17:00Z | 1.6 MB |
| `energy/gb/generation` | 130 | 188,230 | `timestamp` | 2015-12-31T23:30Z | 2026-09-28T17:00Z | 5.3 MB |
| `energy/nyiso/lbmp_da` | 321 | 234,455 | `timestamp` | 2000-01-01T05:00Z | 2026-09-30T03:00Z | 8.5 MB |
| `energy/nyiso/lbmp_rt` | 321 | 233,965 | `timestamp` | 2000-01-01T05:00Z | 2026-09-28T17:00Z | 8.7 MB |
| `energy/weather/era5` | 141 | 4,111,680 | `time` | 2015-01-01T00:00Z | 2026-09-22T23:00Z | 103.4 MB |
| `energy/weather/forecast` | 1 | 17,578 | `issued_at` | 2026-09-27T08:00Z | 2026-09-28T17:00Z | 1.9 MB |
| `energy/weather/observed` | 1 | 4,560 | `time` | 2026-09-24T00:00Z | 2026-09-28T17:00Z | 426.2 KB |

## Backfill progress

| Source | Range | Chunks done | Skipped (no data) | Remaining |
|---|---|---:|---:|---:|
| `aemo` | 1998-12-01 .. 2026-09-27 | 334 / 334 | 0 | complete |
| `airquality` | 2022-08-01 .. 2026-09-27 | 200 / 200 | 0 | complete |
| `eia` | 2015-07-01 .. 2026-09-27 | 43 / 135 | 42 | 50 |
| `eia_bulk` | 2015-07-01 .. 2026-09-27 | 7 / 7 | 0 | complete |
| `eia_market` | 1986-01-01 .. 2026-09-27 | 41 / 41 | 0 | complete |
| `era5` | 2015-01-01 .. 2026-09-27 | 480 / 480 | 0 | complete |
| `europe_power` | 2015-01-01 .. 2026-09-27 | 1381 / 1410 | 0 | 29 |
| `europe_price` | 2015-01-01 .. 2026-09-27 | 141 / 141 | 0 | complete |
| `gb` | 2016-01-01 .. 2026-09-27 | 129 / 129 | 0 | complete |
| `nyiso_da` | 2000-01-01 .. 2026-09-27 | 321 / 321 | 0 | complete |
| `nyiso_rt` | 2000-01-01 .. 2026-09-27 | 321 / 321 | 0 | complete |
