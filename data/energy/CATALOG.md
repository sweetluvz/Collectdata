# Data catalog: `energy`

Auto-generated after every collection run by `scripts/build_catalog.py`.

| Table | Files | Rows | Time column | From | To | Size |
|---|---:|---:|---|---|---|---:|
| `energy/aemo/price_demand` | 336 | 936,271 | `timestamp` | 1998-12-06T16:00Z | 2026-11-05T14:00Z | 29.5 MB |
| `energy/airquality/observed` | 52 | 1,493,944 | `time` | 2022-08-01T00:00Z | 2026-11-06T06:00Z | 23.4 MB |
| `energy/eia/fuel_prices` | 491 | 130,352 | `period` | 1986-01-02 | 2026-11-03 | 1008.2 KB |
| `energy/eia/fuel_type` | 101 | 73,179 | `period` | 2018-07-01T05:00Z | 2026-11-05T07:00Z | 46.4 MB |
| `energy/eia/interchange` | 137 | 99,460 | `period` | 2015-07-01T05:00Z | 2026-11-04T08:00Z | 60.0 MB |
| `energy/eia/region` | 137 | 99,506 | `period` | 2015-07-01T05:00Z | 2026-11-06T06:00Z | 58.9 MB |
| `energy/eia/retail_sales` | 308 | 114,576 | `period` | 2001-01 | 2026-08 | 1.8 MB |
| `energy/eia/subregion` | 95 | 68,769 | `period` | 2019-01-01T00:00Z | 2026-11-05T08:00Z | 12.1 MB |
| `energy/europe/power` | 143 | 2,163,251 | `timestamp` | 2015-01-01T00:00Z | 2026-11-06T05:30Z | 96.0 MB |
| `energy/europe/price` | 143 | 132,818 | `timestamp` | 2015-01-01T00:00Z | 2026-11-06T22:45Z | 4.3 MB |
| `energy/gb/carbon_intensity` | 111 | 160,287 | `timestamp` | 2017-09-11T23:00Z | 2026-11-06T23:30Z | 1015.4 KB |
| `energy/gb/demand` | 130 | 186,321 | `timestamp` | 2016-02-29T23:30Z | 2026-11-06T06:30Z | 1.6 MB |
| `energy/gb/generation` | 132 | 190,081 | `timestamp` | 2015-12-31T23:30Z | 2026-11-06T06:30Z | 5.3 MB |
| `energy/nyiso/lbmp_da` | 323 | 235,368 | `timestamp` | 2000-01-01T05:00Z | 2026-11-07T04:00Z | 8.5 MB |
| `energy/nyiso/lbmp_rt` | 323 | 234,890 | `timestamp` | 2000-01-01T05:00Z | 2026-11-06T06:00Z | 8.7 MB |
| `energy/weather/era5` | 142 | 4,149,120 | `time` | 2015-01-01T00:00Z | 2026-10-31T23:00Z | 102.7 MB |
| `energy/weather/forecast` | 3 | 193,186 | `issued_at` | 2026-09-27T08:00Z | 2026-11-06T06:00Z | 20.9 MB |
| `energy/weather/observed` | 3 | 41,560 | `time` | 2026-09-24T00:00Z | 2026-11-06T06:00Z | 3.8 MB |

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
