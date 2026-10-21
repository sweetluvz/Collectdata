# Data catalog: `energy`

Auto-generated after every collection run by `scripts/build_catalog.py`.

| Table | Files | Rows | Time column | From | To | Size |
|---|---:|---:|---|---|---|---:|
| `energy/aemo/price_demand` | 335 | 931,663 | `timestamp` | 1998-12-06T16:00Z | 2026-10-20T14:00Z | 29.6 MB |
| `energy/airquality/observed` | 51 | 1,478,784 | `time` | 2022-08-01T00:00Z | 2026-10-21T11:00Z | 23.9 MB |
| `energy/eia/fuel_prices` | 490 | 130,184 | `period` | 1986-01-02 | 2026-10-14 | 1016.0 KB |
| `energy/eia/fuel_type` | 100 | 72,794 | `period` | 2018-07-01T05:00Z | 2026-10-20T06:00Z | 46.9 MB |
| `energy/eia/interchange` | 136 | 99,099 | `period` | 2015-07-01T05:00Z | 2026-10-20T07:00Z | 60.3 MB |
| `energy/eia/region` | 136 | 99,127 | `period` | 2015-07-01T05:00Z | 2026-10-21T11:00Z | 59.1 MB |
| `energy/eia/retail_sales` | 307 | 114,204 | `period` | 2001-01 | 2026-07 | 1.8 MB |
| `energy/eia/subregion` | 94 | 68,408 | `period` | 2019-01-01T00:00Z | 2026-10-21T07:00Z | 12.2 MB |
| `energy/europe/power` | 142 | 2,150,424 | `timestamp` | 2015-01-01T00:00Z | 2026-10-21T10:15Z | 96.5 MB |
| `energy/europe/price` | 142 | 131,374 | `timestamp` | 2015-01-01T00:00Z | 2026-10-22T21:45Z | 4.4 MB |
| `energy/gb/carbon_intensity` | 110 | 159,519 | `timestamp` | 2017-09-11T23:00Z | 2026-10-21T23:30Z | 1.0 MB |
| `energy/gb/demand` | 129 | 185,549 | `timestamp` | 2016-02-29T23:30Z | 2026-10-21T04:30Z | 1.6 MB |
| `energy/gb/generation` | 131 | 189,309 | `timestamp` | 2015-12-31T23:30Z | 2026-10-21T04:30Z | 5.3 MB |
| `energy/nyiso/lbmp_da` | 322 | 234,983 | `timestamp` | 2000-01-01T05:00Z | 2026-10-22T03:00Z | 8.5 MB |
| `energy/nyiso/lbmp_rt` | 322 | 234,505 | `timestamp` | 2000-01-01T05:00Z | 2026-10-21T05:00Z | 8.7 MB |
| `energy/weather/era5` | 142 | 4,133,760 | `time` | 2015-01-01T00:00Z | 2026-10-15T23:00Z | 103.4 MB |
| `energy/weather/forecast` | 2 | 125,546 | `issued_at` | 2026-09-27T08:00Z | 2026-10-21T11:00Z | 13.6 MB |
| `energy/weather/observed` | 2 | 26,400 | `time` | 2026-09-24T00:00Z | 2026-10-21T11:00Z | 2.4 MB |

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
