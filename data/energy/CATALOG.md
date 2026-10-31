# Data catalog: `energy`

Auto-generated after every collection run by `scripts/build_catalog.py`.

| Table | Files | Rows | Time column | From | To | Size |
|---|---:|---:|---|---|---|---:|
| `energy/aemo/price_demand` | 335 | 934,543 | `timestamp` | 1998-12-06T16:00Z | 2026-10-30T14:00Z | 29.9 MB |
| `energy/airquality/observed` | 51 | 1,488,424 | `time` | 2022-08-01T00:00Z | 2026-10-31T12:00Z | 24.5 MB |
| `energy/eia/fuel_prices` | 490 | 130,292 | `period` | 1986-01-02 | 2026-10-27 | 1.0 MB |
| `energy/eia/fuel_type` | 100 | 73,058 | `period` | 2018-07-01T05:00Z | 2026-10-31T06:00Z | 47.5 MB |
| `energy/eia/interchange` | 136 | 99,339 | `period` | 2015-07-01T05:00Z | 2026-10-30T07:00Z | 60.8 MB |
| `energy/eia/region` | 136 | 99,368 | `period` | 2015-07-01T05:00Z | 2026-10-31T12:00Z | 59.6 MB |
| `energy/eia/retail_sales` | 308 | 114,576 | `period` | 2001-01 | 2026-08 | 1.8 MB |
| `energy/eia/subregion` | 94 | 68,648 | `period` | 2019-01-01T00:00Z | 2026-10-31T07:00Z | 12.3 MB |
| `energy/europe/power` | 142 | 2,158,490 | `timestamp` | 2015-01-01T00:00Z | 2026-10-31T03:45Z | 97.5 MB |
| `energy/europe/price` | 142 | 132,242 | `timestamp` | 2015-01-01T00:00Z | 2026-10-31T22:45Z | 4.5 MB |
| `energy/gb/carbon_intensity` | 110 | 159,999 | `timestamp` | 2017-09-11T23:00Z | 2026-10-31T23:30Z | 1.0 MB |
| `energy/gb/demand` | 129 | 186,030 | `timestamp` | 2016-02-29T23:30Z | 2026-10-31T05:00Z | 1.6 MB |
| `energy/gb/generation` | 131 | 189,790 | `timestamp` | 2015-12-31T23:30Z | 2026-10-31T05:00Z | 5.4 MB |
| `energy/nyiso/lbmp_da` | 323 | 235,223 | `timestamp` | 2000-01-01T05:00Z | 2026-11-01T03:00Z | 8.5 MB |
| `energy/nyiso/lbmp_rt` | 322 | 234,745 | `timestamp` | 2000-01-01T05:00Z | 2026-10-31T05:00Z | 8.7 MB |
| `energy/weather/era5` | 142 | 4,143,360 | `time` | 2015-01-01T00:00Z | 2026-10-25T23:00Z | 104.2 MB |
| `energy/weather/forecast` | 2 | 174,026 | `issued_at` | 2026-09-27T08:00Z | 2026-10-31T12:00Z | 18.8 MB |
| `energy/weather/observed` | 2 | 36,040 | `time` | 2026-09-24T00:00Z | 2026-10-31T12:00Z | 3.3 MB |

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
