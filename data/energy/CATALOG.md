# Data catalog: `energy`

Auto-generated after every collection run by `scripts/build_catalog.py`.

| Table | Files | Rows | Time column | From | To | Size |
|---|---:|---:|---|---|---|---:|
| `energy/aemo/price_demand` | 336 | 939,727 | `timestamp` | 1998-12-06T16:00Z | 2026-11-17T14:00Z | 29.8 MB |
| `energy/airquality/observed` | 52 | 1,505,104 | `time` | 2022-08-01T00:00Z | 2026-11-17T21:00Z | 24.1 MB |
| `energy/eia/fuel_prices` | 491 | 130,424 | `period` | 1986-01-02 | 2026-11-11 | 1016.6 KB |
| `energy/eia/fuel_type` | 101 | 73,467 | `period` | 2018-07-01T05:00Z | 2026-11-17T07:00Z | 47.2 MB |
| `energy/eia/interchange` | 137 | 99,748 | `period` | 2015-07-01T05:00Z | 2026-11-16T08:00Z | 60.5 MB |
| `energy/eia/region` | 137 | 99,785 | `period` | 2015-07-01T05:00Z | 2026-11-17T21:00Z | 59.4 MB |
| `energy/eia/retail_sales` | 308 | 114,576 | `period` | 2001-01 | 2026-08 | 1.8 MB |
| `energy/eia/subregion` | 95 | 69,057 | `period` | 2019-01-01T00:00Z | 2026-11-17T08:00Z | 12.2 MB |
| `energy/europe/power` | 143 | 2,171,582 | `timestamp` | 2015-01-01T00:00Z | 2026-11-17T19:45Z | 97.1 MB |
| `energy/europe/price` | 143 | 133,970 | `timestamp` | 2015-01-01T00:00Z | 2026-11-18T22:45Z | 4.5 MB |
| `energy/gb/carbon_intensity` | 111 | 160,815 | `timestamp` | 2017-09-11T23:00Z | 2026-11-17T23:30Z | 1.0 MB |
| `energy/gb/demand` | 130 | 186,872 | `timestamp` | 2016-02-29T23:30Z | 2026-11-17T18:00Z | 1.6 MB |
| `energy/gb/generation` | 132 | 190,632 | `timestamp` | 2015-12-31T23:30Z | 2026-11-17T18:00Z | 5.4 MB |
| `energy/nyiso/lbmp_da` | 323 | 235,656 | `timestamp` | 2000-01-01T05:00Z | 2026-11-19T04:00Z | 8.5 MB |
| `energy/nyiso/lbmp_rt` | 323 | 235,169 | `timestamp` | 2000-01-01T05:00Z | 2026-11-17T21:00Z | 8.7 MB |
| `energy/weather/era5` | 143 | 4,159,680 | `time` | 2015-01-01T00:00Z | 2026-11-11T23:00Z | 103.7 MB |
| `energy/weather/forecast` | 3 | 227,746 | `issued_at` | 2026-09-27T08:00Z | 2026-11-17T21:00Z | 24.6 MB |
| `energy/weather/observed` | 3 | 52,720 | `time` | 2026-09-24T00:00Z | 2026-11-17T21:00Z | 4.8 MB |

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
