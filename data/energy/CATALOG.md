# Data catalog: `energy`

Auto-generated after every collection run by `scripts/build_catalog.py`.

| Table | Files | Rows | Time column | From | To | Size |
|---|---:|---:|---|---|---|---:|
| `energy/aemo/price_demand` | 334 | 925,039 | `timestamp` | 1998-12-06T16:00Z | 2026-09-27T14:00Z | 29.5 MB |
| `energy/airquality/observed` | 50 | 1,456,424 | `time` | 2022-08-01T00:00Z | 2026-09-28T04:00Z | 24.0 MB |
| `energy/eia/fuel_prices` | 489 | 129,990 | `period` | 1986-01-02 | 2026-09-22 | 1022.3 KB |
| `energy/eia/fuel_type` | 37 | 26,463 | `period` | 2018-07-01T05:00Z | 2026-09-27T06:00Z | 15.0 MB |
| `energy/eia/interchange` | 73 | 52,744 | `period` | 2015-07-01T05:00Z | 2026-09-26T07:00Z | 29.9 MB |
| `energy/eia/region` | 73 | 52,789 | `period` | 2015-07-01T05:00Z | 2026-09-28T04:00Z | 29.1 MB |
| `energy/eia/retail_sales` | 307 | 114,204 | `period` | 2001-01 | 2026-07 | 1.8 MB |
| `energy/eia/subregion` | 31 | 22,053 | `period` | 2019-01-01T00:00Z | 2026-09-27T07:00Z | 3.6 MB |
| `energy/europe/power` | 25 | 309,640 | `timestamp` | 2015-01-01T00:00Z | 2026-09-28T01:15Z | 13.3 MB |
| `energy/europe/price` | 75 | 54,503 | `timestamp` | 2015-01-01T00:00Z | 2026-09-28T21:45Z | 1.5 MB |
| `energy/gb/carbon_intensity` | 109 | 158,415 | `timestamp` | 2017-09-11T23:00Z | 2026-09-28T23:30Z | 1.0 MB |
| `energy/gb/demand` | 128 | 184,441 | `timestamp` | 2016-02-29T23:30Z | 2026-09-28T02:30Z | 1.6 MB |
| `energy/gb/generation` | 130 | 188,201 | `timestamp` | 2015-12-31T23:30Z | 2026-09-28T02:30Z | 5.3 MB |
| `energy/nyiso/lbmp_da` | 321 | 234,431 | `timestamp` | 2000-01-01T05:00Z | 2026-09-29T03:00Z | 8.5 MB |
| `energy/nyiso/lbmp_rt` | 321 | 233,952 | `timestamp` | 2000-01-01T05:00Z | 2026-09-28T04:00Z | 8.7 MB |
| `energy/weather/era5` | 141 | 4,111,680 | `time` | 2015-01-01T00:00Z | 2026-09-22T23:00Z | 103.4 MB |
| `energy/weather/forecast` | 1 | 10,538 | `issued_at` | 2026-09-27T08:00Z | 2026-09-28T04:00Z | 1.1 MB |
| `energy/weather/observed` | 1 | 4,040 | `time` | 2026-09-24T00:00Z | 2026-09-28T04:00Z | 377.7 KB |

## Backfill progress

| Source | Range | Chunks done | Skipped (no data) | Remaining |
|---|---|---:|---:|---:|
| `aemo` | 1998-12-01 .. 2026-09-27 | 334 / 334 | 0 | complete |
| `airquality` | 2022-08-01 .. 2026-09-27 | 200 / 200 | 0 | complete |
| `eia` | 2015-07-01 .. 2026-09-27 | 30 / 135 | 42 | 63 |
| `eia_bulk` | 2015-07-01 .. 2026-09-27 | 7 / 7 | 0 | complete |
| `eia_market` | 1986-01-01 .. 2026-09-27 | 41 / 41 | 0 | complete |
| `era5` | 2015-01-01 .. 2026-09-27 | 480 / 480 | 0 | complete |
| `europe_power` | 2015-01-01 .. 2026-09-27 | 239 / 1410 | 0 | 1171 |
| `europe_price` | 2015-01-01 .. 2026-09-27 | 74 / 141 | 0 | 67 |
| `gb` | 2016-01-01 .. 2026-09-27 | 129 / 129 | 0 | complete |
| `nyiso_da` | 2000-01-01 .. 2026-09-27 | 321 / 321 | 0 | complete |
| `nyiso_rt` | 2000-01-01 .. 2026-09-27 | 321 / 321 | 0 | complete |
