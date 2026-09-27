# Data catalog: `energy`

Auto-generated after every collection run by `scripts/build_catalog.py`.

| Table | Files | Rows | Time column | From | To | Size |
|---|---:|---:|---|---|---|---:|
| `energy/airquality/observed` | 1 | 3,320 | `time` | 2026-09-24T00:00Z | 2026-09-27T10:00Z | 208.1 KB |
| `energy/eia/fuel_prices` | 4 | 721 | `period` | 2026-06-29 | 2026-09-22 | 82.7 KB |
| `energy/eia/fuel_type` | 6 | 3,788 | `period` | 2019-01-01T00:00Z | 2026-09-27T06:00Z | 2.5 MB |
| `energy/eia/interchange` | 6 | 3,765 | `period` | 2019-01-01T00:00Z | 2026-09-26T07:00Z | 2.5 MB |
| `energy/eia/region` | 6 | 3,793 | `period` | 2019-01-01T00:00Z | 2026-09-27T11:00Z | 2.5 MB |
| `energy/eia/retail_sales` | 2 | 744 | `period` | 2026-06 | 2026-07 | 22.1 KB |
| `energy/eia/subregion` | 6 | 3,789 | `period` | 2019-01-01T00:00Z | 2026-09-27T07:00Z | 633.5 KB |
| `energy/europe/power` | 20 | 234,169 | `timestamp` | 2015-01-01T00:00Z | 2026-09-27T11:15Z | 10.2 MB |
| `energy/europe/price` | 1 | 480 | `timestamp` | 2026-09-23T22:00Z | 2026-09-28T21:45Z | 47.1 KB |
| `energy/weather/era5` | 97 | 2,425,128 | `time` | 2015-01-01T00:00Z | 2026-09-21T23:00Z | 58.7 MB |
| `energy/weather/forecast` | 1 | 2,338 | `issued_at` | 2026-09-27T08:00Z | 2026-09-27T10:00Z | 260.1 KB |
| `energy/weather/observed` | 1 | 3,320 | `time` | 2026-09-24T00:00Z | 2026-09-27T10:00Z | 310.3 KB |

## Backfill progress

| Source | Range | Chunks done | Skipped (no data) | Remaining |
|---|---|---:|---:|---:|
| `airquality` | 2022-08-01 .. 2026-09-27 | 0 / 200 | 0 | 200 |
| `eia` | 2015-07-01 .. 2026-09-27 | 5 / 135 | 42 | 88 |
| `eia_market` | 1986-01-01 .. 2026-09-27 | 0 / 41 | 0 | 41 |
| `era5` | 2015-01-01 .. 2026-09-27 | 275 / 480 | 0 | 205 |
| `europe_power` | 2015-01-01 .. 2026-09-27 | 185 / 1410 | 0 | 1225 |
| `europe_price` | 2015-01-01 .. 2026-09-27 | 0 / 141 | 0 | 141 |
