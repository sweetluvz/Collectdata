# Data catalog: `energy`

Auto-generated after every collection run by `scripts/build_catalog.py`.

| Table | Files | Rows | Time column | From | To | Size |
|---|---:|---:|---|---|---|---:|
| `energy/aemo/price_demand` | 334 | 925,615 | `timestamp` | 1998-12-06T16:00Z | 2026-09-29T14:00Z | 29.6 MB |
| `energy/airquality/observed` | 50 | 1,458,384 | `time` | 2022-08-01T00:00Z | 2026-09-30T05:00Z | 24.1 MB |
| `energy/eia/fuel_prices` | 489 | 129,990 | `period` | 1986-01-02 | 2026-09-22 | 1022.3 KB |
| `energy/eia/fuel_type` | 99 | 72,290 | `period` | 2018-07-01T05:00Z | 2026-09-29T06:00Z | 47.0 MB |
| `energy/eia/interchange` | 135 | 98,571 | `period` | 2015-07-01T05:00Z | 2026-09-28T07:00Z | 60.2 MB |
| `energy/eia/region` | 135 | 98,617 | `period` | 2015-07-01T05:00Z | 2026-09-30T05:00Z | 59.1 MB |
| `energy/eia/retail_sales` | 307 | 114,204 | `period` | 2001-01 | 2026-07 | 1.8 MB |
| `energy/eia/subregion` | 93 | 67,880 | `period` | 2019-01-01T00:00Z | 2026-09-29T07:00Z | 12.2 MB |
| `energy/europe/power` | 141 | 2,132,948 | `timestamp` | 2015-01-01T00:00Z | 2026-09-29T21:00Z | 96.4 MB |
| `energy/europe/price` | 141 | 129,262 | `timestamp` | 2015-01-01T00:00Z | 2026-09-30T21:45Z | 4.4 MB |
| `energy/gb/carbon_intensity` | 109 | 158,463 | `timestamp` | 2017-09-11T23:00Z | 2026-09-29T23:30Z | 1.0 MB |
| `energy/gb/demand` | 128 | 184,527 | `timestamp` | 2016-02-29T23:30Z | 2026-09-29T21:30Z | 1.6 MB |
| `energy/gb/generation` | 130 | 188,287 | `timestamp` | 2015-12-31T23:30Z | 2026-09-29T21:30Z | 5.3 MB |
| `energy/nyiso/lbmp_da` | 322 | 234,479 | `timestamp` | 2000-01-01T05:00Z | 2026-10-01T03:00Z | 8.5 MB |
| `energy/nyiso/lbmp_rt` | 321 | 233,994 | `timestamp` | 2000-01-01T05:00Z | 2026-09-29T22:00Z | 8.7 MB |
| `energy/weather/era5` | 141 | 4,113,600 | `time` | 2015-01-01T00:00Z | 2026-09-24T23:00Z | 103.5 MB |
| `energy/weather/forecast` | 1 | 30,738 | `issued_at` | 2026-09-27T08:00Z | 2026-09-30T05:00Z | 3.3 MB |
| `energy/weather/observed` | 1 | 6,000 | `time` | 2026-09-24T00:00Z | 2026-09-30T05:00Z | 561.1 KB |

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
