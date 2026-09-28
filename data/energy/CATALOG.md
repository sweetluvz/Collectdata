# Data catalog: `energy`

Auto-generated after every collection run by `scripts/build_catalog.py`.

| Table | Files | Rows | Time column | From | To | Size |
|---|---:|---:|---|---|---|---:|
| `energy/aemo/price_demand` | 334 | 925,039 | `timestamp` | 1998-12-06T16:00Z | 2026-09-27T14:00Z | 29.5 MB |
| `energy/airquality/observed` | 50 | 1,456,624 | `time` | 2022-08-01T00:00Z | 2026-09-28T09:00Z | 24.0 MB |
| `energy/eia/fuel_prices` | 489 | 129,990 | `period` | 1986-01-02 | 2026-09-22 | 1022.3 KB |
| `energy/eia/fuel_type` | 45 | 32,295 | `period` | 2018-07-01T05:00Z | 2026-09-27T06:00Z | 18.4 MB |
| `energy/eia/interchange` | 81 | 58,599 | `period` | 2015-07-01T05:00Z | 2026-09-27T06:00Z | 33.6 MB |
| `energy/eia/region` | 81 | 58,626 | `period` | 2015-07-01T05:00Z | 2026-09-28T09:00Z | 32.7 MB |
| `energy/eia/retail_sales` | 307 | 114,204 | `period` | 2001-01 | 2026-07 | 1.8 MB |
| `energy/eia/subregion` | 39 | 27,908 | `period` | 2019-01-01T00:00Z | 2026-09-28T06:00Z | 4.6 MB |
| `energy/europe/power` | 28 | 351,584 | `timestamp` | 2015-01-01T00:00Z | 2026-09-28T06:30Z | 15.1 MB |
| `energy/europe/price` | 123 | 89,567 | `timestamp` | 2015-01-01T00:00Z | 2026-09-28T21:45Z | 2.6 MB |
| `energy/gb/carbon_intensity` | 109 | 158,415 | `timestamp` | 2017-09-11T23:00Z | 2026-09-28T23:30Z | 1.0 MB |
| `energy/gb/demand` | 128 | 184,448 | `timestamp` | 2016-02-29T23:30Z | 2026-09-28T06:00Z | 1.6 MB |
| `energy/gb/generation` | 130 | 188,208 | `timestamp` | 2015-12-31T23:30Z | 2026-09-28T06:00Z | 5.3 MB |
| `energy/nyiso/lbmp_da` | 321 | 234,431 | `timestamp` | 2000-01-01T05:00Z | 2026-09-29T03:00Z | 8.5 MB |
| `energy/nyiso/lbmp_rt` | 321 | 233,957 | `timestamp` | 2000-01-01T05:00Z | 2026-09-28T09:00Z | 8.7 MB |
| `energy/weather/era5` | 141 | 4,111,680 | `time` | 2015-01-01T00:00Z | 2026-09-22T23:00Z | 103.4 MB |
| `energy/weather/forecast` | 1 | 13,698 | `issued_at` | 2026-09-27T08:00Z | 2026-09-28T09:00Z | 1.5 MB |
| `energy/weather/observed` | 1 | 4,240 | `time` | 2026-09-24T00:00Z | 2026-09-28T09:00Z | 396.2 KB |

## Backfill progress

| Source | Range | Chunks done | Skipped (no data) | Remaining |
|---|---|---:|---:|---:|
| `aemo` | 1998-12-01 .. 2026-09-27 | 334 / 334 | 0 | complete |
| `airquality` | 2022-08-01 .. 2026-09-27 | 200 / 200 | 0 | complete |
| `eia` | 2015-07-01 .. 2026-09-27 | 38 / 135 | 42 | 55 |
| `eia_bulk` | 2015-07-01 .. 2026-09-27 | 7 / 7 | 0 | complete |
| `eia_market` | 1986-01-01 .. 2026-09-27 | 41 / 41 | 0 | complete |
| `era5` | 2015-01-01 .. 2026-09-27 | 480 / 480 | 0 | complete |
| `europe_power` | 2015-01-01 .. 2026-09-27 | 270 / 1410 | 0 | 1140 |
| `europe_price` | 2015-01-01 .. 2026-09-27 | 122 / 141 | 0 | 19 |
| `gb` | 2016-01-01 .. 2026-09-27 | 129 / 129 | 0 | complete |
| `nyiso_da` | 2000-01-01 .. 2026-09-27 | 321 / 321 | 0 | complete |
| `nyiso_rt` | 2000-01-01 .. 2026-09-27 | 321 / 321 | 0 | complete |
