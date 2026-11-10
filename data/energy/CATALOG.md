# Data catalog: `energy`

Auto-generated after every collection run by `scripts/build_catalog.py`.

| Table | Files | Rows | Time column | From | To | Size |
|---|---:|---:|---|---|---|---:|
| `energy/aemo/price_demand` | 336 | 937,423 | `timestamp` | 1998-12-06T16:00Z | 2026-11-09T14:00Z | 29.6 MB |
| `energy/airquality/observed` | 52 | 1,497,824 | `time` | 2022-08-01T00:00Z | 2026-11-10T07:00Z | 23.7 MB |
| `energy/eia/fuel_prices` | 491 | 130,352 | `period` | 1986-01-02 | 2026-11-03 | 1008.2 KB |
| `energy/eia/fuel_type` | 101 | 73,275 | `period` | 2018-07-01T05:00Z | 2026-11-09T07:00Z | 46.7 MB |
| `energy/eia/interchange` | 137 | 99,556 | `period` | 2015-07-01T05:00Z | 2026-11-08T08:00Z | 60.2 MB |
| `energy/eia/region` | 137 | 99,603 | `period` | 2015-07-01T05:00Z | 2026-11-10T07:00Z | 59.1 MB |
| `energy/eia/retail_sales` | 308 | 114,576 | `period` | 2001-01 | 2026-08 | 1.8 MB |
| `energy/eia/subregion` | 95 | 68,865 | `period` | 2019-01-01T00:00Z | 2026-11-09T08:00Z | 12.1 MB |
| `energy/europe/power` | 143 | 2,166,126 | `timestamp` | 2015-01-01T00:00Z | 2026-11-10T05:45Z | 96.3 MB |
| `energy/europe/price` | 143 | 133,202 | `timestamp` | 2015-01-01T00:00Z | 2026-11-10T22:45Z | 4.4 MB |
| `energy/gb/carbon_intensity` | 111 | 160,479 | `timestamp` | 2017-09-11T23:00Z | 2026-11-10T23:30Z | 1022.5 KB |
| `energy/gb/demand` | 130 | 186,513 | `timestamp` | 2016-02-29T23:30Z | 2026-11-10T06:30Z | 1.6 MB |
| `energy/gb/generation` | 132 | 190,274 | `timestamp` | 2015-12-31T23:30Z | 2026-11-10T07:00Z | 5.3 MB |
| `energy/nyiso/lbmp_da` | 323 | 235,464 | `timestamp` | 2000-01-01T05:00Z | 2026-11-11T04:00Z | 8.5 MB |
| `energy/nyiso/lbmp_rt` | 323 | 234,987 | `timestamp` | 2000-01-01T05:00Z | 2026-11-10T07:00Z | 8.7 MB |
| `energy/weather/era5` | 143 | 4,152,960 | `time` | 2015-01-01T00:00Z | 2026-11-04T23:00Z | 103.1 MB |
| `energy/weather/forecast` | 3 | 206,586 | `issued_at` | 2026-09-27T08:00Z | 2026-11-10T07:00Z | 22.3 MB |
| `energy/weather/observed` | 3 | 45,440 | `time` | 2026-09-24T00:00Z | 2026-11-10T07:00Z | 4.1 MB |

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
