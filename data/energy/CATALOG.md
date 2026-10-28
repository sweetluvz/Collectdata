# Data catalog: `energy`

Auto-generated after every collection run by `scripts/build_catalog.py`.

| Table | Files | Rows | Time column | From | To | Size |
|---|---:|---:|---|---|---|---:|
| `energy/aemo/price_demand` | 335 | 933,679 | `timestamp` | 1998-12-06T16:00Z | 2026-10-27T14:00Z | 29.8 MB |
| `energy/airquality/observed` | 51 | 1,485,944 | `time` | 2022-08-01T00:00Z | 2026-10-28T22:00Z | 24.4 MB |
| `energy/eia/fuel_prices` | 490 | 130,292 | `period` | 1986-01-02 | 2026-10-27 | 1.0 MB |
| `energy/eia/fuel_type` | 100 | 72,986 | `period` | 2018-07-01T05:00Z | 2026-10-28T06:00Z | 47.4 MB |
| `energy/eia/interchange` | 136 | 99,267 | `period` | 2015-07-01T05:00Z | 2026-10-27T07:00Z | 60.6 MB |
| `energy/eia/region` | 136 | 99,306 | `period` | 2015-07-01T05:00Z | 2026-10-28T22:00Z | 59.5 MB |
| `energy/eia/retail_sales` | 308 | 114,576 | `period` | 2001-01 | 2026-08 | 1.8 MB |
| `energy/eia/subregion` | 94 | 68,576 | `period` | 2019-01-01T00:00Z | 2026-10-28T07:00Z | 12.3 MB |
| `energy/europe/power` | 142 | 2,156,599 | `timestamp` | 2015-01-01T00:00Z | 2026-10-28T20:45Z | 97.3 MB |
| `energy/europe/price` | 142 | 132,050 | `timestamp` | 2015-01-01T00:00Z | 2026-10-29T22:45Z | 4.5 MB |
| `energy/gb/carbon_intensity` | 110 | 159,855 | `timestamp` | 2017-09-11T23:00Z | 2026-10-28T23:30Z | 1.0 MB |
| `energy/gb/demand` | 129 | 185,901 | `timestamp` | 2016-02-29T23:30Z | 2026-10-28T12:30Z | 1.6 MB |
| `energy/gb/generation` | 131 | 189,661 | `timestamp` | 2015-12-31T23:30Z | 2026-10-28T12:30Z | 5.4 MB |
| `energy/nyiso/lbmp_da` | 322 | 235,151 | `timestamp` | 2000-01-01T05:00Z | 2026-10-29T03:00Z | 8.5 MB |
| `energy/nyiso/lbmp_rt` | 322 | 234,681 | `timestamp` | 2000-01-01T05:00Z | 2026-10-28T13:00Z | 8.7 MB |
| `energy/weather/era5` | 142 | 4,140,480 | `time` | 2015-01-01T00:00Z | 2026-10-22T23:00Z | 104.0 MB |
| `energy/weather/forecast` | 2 | 162,866 | `issued_at` | 2026-09-27T08:00Z | 2026-10-28T22:00Z | 17.6 MB |
| `energy/weather/observed` | 2 | 33,560 | `time` | 2026-09-24T00:00Z | 2026-10-28T22:00Z | 3.0 MB |

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
