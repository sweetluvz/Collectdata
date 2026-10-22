# Data catalog: `energy`

Auto-generated after every collection run by `scripts/build_catalog.py`.

| Table | Files | Rows | Time column | From | To | Size |
|---|---:|---:|---|---|---|---:|
| `energy/aemo/price_demand` | 335 | 931,951 | `timestamp` | 1998-12-06T16:00Z | 2026-10-21T14:00Z | 29.6 MB |
| `energy/airquality/observed` | 51 | 1,479,464 | `time` | 2022-08-01T00:00Z | 2026-10-22T04:00Z | 24.0 MB |
| `energy/eia/fuel_prices` | 490 | 130,232 | `period` | 1986-01-02 | 2026-10-20 | 1021.7 KB |
| `energy/eia/fuel_type` | 100 | 72,818 | `period` | 2018-07-01T05:00Z | 2026-10-21T06:00Z | 46.9 MB |
| `energy/eia/interchange` | 136 | 99,099 | `period` | 2015-07-01T05:00Z | 2026-10-20T07:00Z | 60.3 MB |
| `energy/eia/region` | 136 | 99,137 | `period` | 2015-07-01T05:00Z | 2026-10-21T21:00Z | 59.2 MB |
| `energy/eia/retail_sales` | 307 | 114,204 | `period` | 2001-01 | 2026-07 | 1.8 MB |
| `energy/eia/subregion` | 94 | 68,408 | `period` | 2019-01-01T00:00Z | 2026-10-21T07:00Z | 12.2 MB |
| `energy/europe/power` | 142 | 2,150,882 | `timestamp` | 2015-01-01T00:00Z | 2026-10-21T20:00Z | 96.5 MB |
| `energy/europe/price` | 142 | 131,374 | `timestamp` | 2015-01-01T00:00Z | 2026-10-22T21:45Z | 4.4 MB |
| `energy/gb/carbon_intensity` | 110 | 159,519 | `timestamp` | 2017-09-11T23:00Z | 2026-10-21T23:30Z | 1.0 MB |
| `energy/gb/demand` | 129 | 185,582 | `timestamp` | 2016-02-29T23:30Z | 2026-10-21T21:00Z | 1.6 MB |
| `energy/gb/generation` | 131 | 189,342 | `timestamp` | 2015-12-31T23:30Z | 2026-10-21T21:00Z | 5.3 MB |
| `energy/nyiso/lbmp_da` | 322 | 235,007 | `timestamp` | 2000-01-01T05:00Z | 2026-10-23T03:00Z | 8.5 MB |
| `energy/nyiso/lbmp_rt` | 322 | 234,521 | `timestamp` | 2000-01-01T05:00Z | 2026-10-21T21:00Z | 8.7 MB |
| `energy/weather/era5` | 142 | 4,134,720 | `time` | 2015-01-01T00:00Z | 2026-10-16T23:00Z | 103.5 MB |
| `energy/weather/forecast` | 2 | 129,506 | `issued_at` | 2026-09-27T08:00Z | 2026-10-22T04:00Z | 14.0 MB |
| `energy/weather/observed` | 2 | 27,080 | `time` | 2026-09-24T00:00Z | 2026-10-22T04:00Z | 2.5 MB |

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
