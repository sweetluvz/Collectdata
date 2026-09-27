# Data catalog: `energy`

Auto-generated after every collection run by `scripts/build_catalog.py`.

| Table | Files | Rows | Time column | From | To | Size |
|---|---:|---:|---|---|---|---:|
| `energy/aemo/price_demand` | 3 | 16,416 | `timestamp` | 2026-07-31T14:05Z | 2026-09-26T14:00Z | 1.4 MB |
| `energy/airquality/observed` | 6 | 7,040 | `time` | 2022-08-04T00:00Z | 2026-09-27T13:00Z | 274.4 KB |
| `energy/eia/fuel_prices` | 4 | 721 | `period` | 2026-06-29 | 2026-09-22 | 82.7 KB |
| `energy/eia/fuel_type` | 6 | 3,788 | `period` | 2019-01-01T00:00Z | 2026-09-27T06:00Z | 2.5 MB |
| `energy/eia/interchange` | 6 | 3,765 | `period` | 2019-01-01T00:00Z | 2026-09-26T07:00Z | 2.5 MB |
| `energy/eia/region` | 6 | 3,793 | `period` | 2019-01-01T00:00Z | 2026-09-27T11:00Z | 2.5 MB |
| `energy/eia/retail_sales` | 2 | 744 | `period` | 2026-06 | 2026-07 | 22.1 KB |
| `energy/eia/subregion` | 6 | 3,789 | `period` | 2019-01-01T00:00Z | 2026-09-27T07:00Z | 633.5 KB |
| `energy/europe/power` | 20 | 234,169 | `timestamp` | 2015-01-01T00:00Z | 2026-09-27T11:15Z | 10.2 MB |
| `energy/europe/price` | 1 | 480 | `timestamp` | 2026-09-23T22:00Z | 2026-09-28T21:45Z | 47.1 KB |
| `energy/gb/carbon_intensity` | 1 | 337 | `timestamp` | 2026-09-20T23:30Z | 2026-09-27T23:30Z | 11.3 KB |
| `energy/gb/demand` | 1 | 317 | `timestamp` | 2026-09-20T23:00Z | 2026-09-27T13:00Z | 9.3 KB |
| `energy/gb/generation` | 3 | 1,805 | `timestamp` | 2015-12-31T23:30Z | 2026-09-27T13:00Z | 67.5 KB |
| `energy/nyiso/lbmp_da` | 321 | 234,431 | `timestamp` | 2000-01-01T05:00Z | 2026-09-29T03:00Z | 8.5 MB |
| `energy/nyiso/lbmp_rt` | 141 | 102,441 | `timestamp` | 2015-01-01T05:00Z | 2026-09-27T13:00Z | 3.8 MB |
| `energy/weather/era5` | 121 | 3,354,384 | `time` | 2015-01-01T00:00Z | 2026-09-21T23:00Z | 80.9 MB |
| `energy/weather/forecast` | 1 | 3,698 | `issued_at` | 2026-09-27T08:00Z | 2026-09-27T13:00Z | 411.5 KB |
| `energy/weather/observed` | 1 | 3,440 | `time` | 2026-09-24T00:00Z | 2026-09-27T13:00Z | 321.5 KB |

## Backfill progress

| Source | Range | Chunks done | Skipped (no data) | Remaining |
|---|---|---:|---:|---:|
| `aemo` | 1998-12-01 .. 2026-09-27 | 0 / 334 | 0 | 334 |
| `airquality` | 2022-08-01 .. 2026-09-27 | 1 / 200 | 0 | 199 |
| `eia` | 2015-07-01 .. 2026-09-27 | 5 / 135 | 42 | 88 |
| `eia_market` | 1986-01-01 .. 2026-09-27 | 0 / 41 | 0 | 41 |
| `era5` | 2015-01-01 .. 2026-09-27 | 381 / 480 | 0 | 99 |
| `europe_power` | 2015-01-01 .. 2026-09-27 | 185 / 1410 | 0 | 1225 |
| `europe_price` | 2015-01-01 .. 2026-09-27 | 0 / 141 | 0 | 141 |
| `gb` | 2016-01-01 .. 2026-09-27 | 0 / 129 | 0 | 129 |
| `nyiso_da` | 2000-01-01 .. 2026-09-27 | 321 / 321 | 0 | complete |
| `nyiso_rt` | 2015-01-01 .. 2026-09-27 | 141 / 141 | 0 | complete |
