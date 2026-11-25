# Data catalog: `energy`

Auto-generated after every collection run by `scripts/build_catalog.py`.

| Table | Files | Rows | Time column | From | To | Size |
|---|---:|---:|---|---|---|---:|
| `energy/aemo/price_demand` | 336 | 941,743 | `timestamp` | 1998-12-06T16:00Z | 2026-11-24T14:00Z | 30.0 MB |
| `energy/airquality/observed` | 52 | 1,512,784 | `time` | 2022-08-01T00:00Z | 2026-11-25T21:00Z | 24.6 MB |
| `energy/eia/fuel_prices` | 491 | 130,532 | `period` | 1986-01-02 | 2026-11-24 | 1.0 MB |
| `energy/eia/fuel_type` | 101 | 73,659 | `period` | 2018-07-01T05:00Z | 2026-11-25T07:00Z | 47.7 MB |
| `energy/eia/interchange` | 137 | 99,940 | `period` | 2015-07-01T05:00Z | 2026-11-24T08:00Z | 60.9 MB |
| `energy/eia/region` | 137 | 99,977 | `period` | 2015-07-01T05:00Z | 2026-11-25T21:00Z | 59.8 MB |
| `energy/eia/retail_sales` | 309 | 114,948 | `period` | 2001-01 | 2026-09 | 1.8 MB |
| `energy/eia/subregion` | 95 | 69,249 | `period` | 2019-01-01T00:00Z | 2026-11-25T08:00Z | 12.3 MB |
| `energy/europe/power` | 143 | 2,177,379 | `timestamp` | 2015-01-01T00:00Z | 2026-11-25T20:15Z | 97.8 MB |
| `energy/europe/price` | 143 | 134,738 | `timestamp` | 2015-01-01T00:00Z | 2026-11-26T22:45Z | 4.5 MB |
| `energy/gb/carbon_intensity` | 111 | 161,199 | `timestamp` | 2017-09-11T23:00Z | 2026-11-25T23:30Z | 1.0 MB |
| `energy/gb/demand` | 130 | 187,236 | `timestamp` | 2016-02-29T23:30Z | 2026-11-25T08:00Z | 1.6 MB |
| `energy/gb/generation` | 132 | 190,996 | `timestamp` | 2015-12-31T23:30Z | 2026-11-25T08:00Z | 5.4 MB |
| `energy/nyiso/lbmp_da` | 323 | 235,824 | `timestamp` | 2000-01-01T05:00Z | 2026-11-26T04:00Z | 8.5 MB |
| `energy/nyiso/lbmp_rt` | 323 | 235,348 | `timestamp` | 2000-01-01T05:00Z | 2026-11-25T08:00Z | 8.7 MB |
| `energy/weather/era5` | 143 | 4,167,360 | `time` | 2015-01-01T00:00Z | 2026-11-19T23:00Z | 104.4 MB |
| `energy/weather/forecast` | 3 | 247,786 | `issued_at` | 2026-09-27T08:00Z | 2026-11-25T21:00Z | 26.7 MB |
| `energy/weather/observed` | 3 | 60,400 | `time` | 2026-09-24T00:00Z | 2026-11-25T21:00Z | 5.5 MB |

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
