# Data catalog: `energy`

Auto-generated after every collection run by `scripts/build_catalog.py`.

| Table | Files | Rows | Time column | From | To | Size |
|---|---:|---:|---|---|---|---:|
| `energy/aemo/price_demand` | 334 | 925,903 | `timestamp` | 1998-12-06T16:00Z | 2026-09-30T14:00Z | 29.1 MB |
| `energy/airquality/observed` | 51 | 1,459,664 | `time` | 2022-08-01T00:00Z | 2026-10-01T13:00Z | 22.8 MB |
| `energy/eia/fuel_prices` | 489 | 130,050 | `period` | 1986-01-02 | 2026-09-29 | 1000.3 KB |
| `energy/eia/fuel_type` | 100 | 72,338 | `period` | 2018-07-01T05:00Z | 2026-10-01T06:00Z | 45.7 MB |
| `energy/eia/interchange` | 135 | 98,619 | `period` | 2015-07-01T05:00Z | 2026-09-30T07:00Z | 59.3 MB |
| `energy/eia/region` | 136 | 98,649 | `period` | 2015-07-01T05:00Z | 2026-10-01T13:00Z | 58.2 MB |
| `energy/eia/retail_sales` | 307 | 114,204 | `period` | 2001-01 | 2026-07 | 1.8 MB |
| `energy/eia/subregion` | 94 | 67,928 | `period` | 2019-01-01T00:00Z | 2026-10-01T07:00Z | 11.9 MB |
| `energy/europe/power` | 142 | 2,134,281 | `timestamp` | 2015-01-01T00:00Z | 2026-10-01T12:00Z | 94.4 MB |
| `energy/europe/price` | 142 | 129,454 | `timestamp` | 2015-01-01T00:00Z | 2026-10-02T21:45Z | 4.2 MB |
| `energy/gb/carbon_intensity` | 110 | 158,559 | `timestamp` | 2017-09-11T23:00Z | 2026-10-01T23:30Z | 996.9 KB |
| `energy/gb/demand` | 129 | 184,606 | `timestamp` | 2016-02-29T23:30Z | 2026-10-01T13:00Z | 1.6 MB |
| `energy/gb/generation` | 131 | 188,366 | `timestamp` | 2015-12-31T23:30Z | 2026-10-01T13:00Z | 5.3 MB |
| `energy/nyiso/lbmp_da` | 322 | 234,527 | `timestamp` | 2000-01-01T05:00Z | 2026-10-03T03:00Z | 8.4 MB |
| `energy/nyiso/lbmp_rt` | 322 | 234,033 | `timestamp` | 2000-01-01T05:00Z | 2026-10-01T13:00Z | 8.7 MB |
| `energy/weather/era5` | 141 | 4,114,560 | `time` | 2015-01-01T00:00Z | 2026-09-25T23:00Z | 101.6 MB |
| `energy/weather/forecast` | 2 | 36,138 | `issued_at` | 2026-09-27T08:00Z | 2026-10-01T13:00Z | 3.9 MB |
| `energy/weather/observed` | 2 | 7,280 | `time` | 2026-09-24T00:00Z | 2026-10-01T13:00Z | 681.4 KB |

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
