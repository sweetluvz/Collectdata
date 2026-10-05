# Data catalog: `energy`

Auto-generated after every collection run by `scripts/build_catalog.py`.

| Table | Files | Rows | Time column | From | To | Size |
|---|---:|---:|---|---|---|---:|
| `energy/aemo/price_demand` | 335 | 927,055 | `timestamp` | 1998-12-06T16:00Z | 2026-10-04T14:00Z | 29.2 MB |
| `energy/airquality/observed` | 51 | 1,463,184 | `time` | 2022-08-01T00:00Z | 2026-10-05T05:00Z | 23.0 MB |
| `energy/eia/fuel_prices` | 489 | 130,050 | `period` | 1986-01-02 | 2026-09-29 | 1000.3 KB |
| `energy/eia/fuel_type` | 100 | 72,410 | `period` | 2018-07-01T05:00Z | 2026-10-04T06:00Z | 45.9 MB |
| `energy/eia/interchange` | 136 | 98,691 | `period` | 2015-07-01T05:00Z | 2026-10-03T07:00Z | 59.5 MB |
| `energy/eia/region` | 136 | 98,737 | `period` | 2015-07-01T05:00Z | 2026-10-05T05:00Z | 58.4 MB |
| `energy/eia/retail_sales` | 307 | 114,204 | `period` | 2001-01 | 2026-07 | 1.8 MB |
| `energy/eia/subregion` | 94 | 68,000 | `period` | 2019-01-01T00:00Z | 2026-10-04T07:00Z | 12.0 MB |
| `energy/europe/power` | 142 | 2,136,193 | `timestamp` | 2015-01-01T00:00Z | 2026-10-03T20:00Z | 94.6 MB |
| `energy/europe/price` | 142 | 129,646 | `timestamp` | 2015-01-01T00:00Z | 2026-10-04T21:45Z | 4.2 MB |
| `energy/gb/carbon_intensity` | 110 | 158,751 | `timestamp` | 2017-09-11T23:00Z | 2026-10-05T23:30Z | 1003.3 KB |
| `energy/gb/demand` | 129 | 184,783 | `timestamp` | 2016-02-29T23:30Z | 2026-10-05T05:30Z | 1.6 MB |
| `energy/gb/generation` | 131 | 188,543 | `timestamp` | 2015-12-31T23:30Z | 2026-10-05T05:30Z | 5.3 MB |
| `energy/nyiso/lbmp_da` | 322 | 234,599 | `timestamp` | 2000-01-01T05:00Z | 2026-10-06T03:00Z | 8.4 MB |
| `energy/nyiso/lbmp_rt` | 322 | 234,122 | `timestamp` | 2000-01-01T05:00Z | 2026-10-05T06:00Z | 8.7 MB |
| `energy/weather/era5` | 141 | 4,118,400 | `time` | 2015-01-01T00:00Z | 2026-09-29T23:00Z | 102.0 MB |
| `energy/weather/forecast` | 2 | 52,418 | `issued_at` | 2026-09-27T08:00Z | 2026-10-05T05:00Z | 5.7 MB |
| `energy/weather/observed` | 2 | 10,800 | `time` | 2026-09-24T00:00Z | 2026-10-05T05:00Z | 1009.9 KB |

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
