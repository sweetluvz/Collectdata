# Data catalog: `energy`

Auto-generated after every collection run by `scripts/build_catalog.py`.

| Table | Files | Rows | Time column | From | To | Size |
|---|---:|---:|---|---|---|---:|
| `energy/aemo/price_demand` | 218 | 330,559 | `timestamp` | 1998-12-06T16:00Z | 2026-09-27T14:00Z | 11.0 MB |
| `energy/airquality/observed` | 30 | 823,992 | `time` | 2022-08-01T00:00Z | 2026-09-27T20:00Z | 11.4 MB |
| `energy/eia/fuel_prices` | 489 | 129,990 | `period` | 1986-01-02 | 2026-09-22 | 1022.3 KB |
| `energy/eia/fuel_type` | 18 | 12,591 | `period` | 2018-07-01T05:00Z | 2026-09-27T06:00Z | 6.9 MB |
| `energy/eia/interchange` | 53 | 38,152 | `period` | 2015-07-01T05:00Z | 2026-09-26T07:00Z | 21.0 MB |
| `energy/eia/region` | 54 | 38,910 | `period` | 2015-07-01T05:00Z | 2026-09-27T21:00Z | 20.7 MB |
| `energy/eia/retail_sales` | 307 | 114,204 | `period` | 2001-01 | 2026-07 | 1.8 MB |
| `energy/eia/subregion` | 11 | 7,461 | `period` | 2019-01-01T00:00Z | 2026-09-27T07:00Z | 1.2 MB |
| `energy/europe/power` | 22 | 262,403 | `timestamp` | 2015-01-01T00:00Z | 2026-09-27T17:45Z | 11.4 MB |
| `energy/europe/price` | 26 | 18,767 | `timestamp` | 2015-01-01T00:00Z | 2026-09-28T21:45Z | 470.8 KB |
| `energy/gb/carbon_intensity` | 109 | 158,367 | `timestamp` | 2017-09-11T23:00Z | 2026-09-27T23:30Z | 1.0 MB |
| `energy/gb/demand` | 128 | 184,426 | `timestamp` | 2016-02-29T23:30Z | 2026-09-27T19:00Z | 1.6 MB |
| `energy/gb/generation` | 130 | 188,186 | `timestamp` | 2015-12-31T23:30Z | 2026-09-27T19:00Z | 5.3 MB |
| `energy/nyiso/lbmp_da` | 321 | 234,431 | `timestamp` | 2000-01-01T05:00Z | 2026-09-29T03:00Z | 8.5 MB |
| `energy/nyiso/lbmp_rt` | 321 | 233,944 | `timestamp` | 2000-01-01T05:00Z | 2026-09-27T20:00Z | 8.7 MB |
| `energy/weather/era5` | 141 | 4,110,720 | `time` | 2015-01-01T00:00Z | 2026-09-21T23:00Z | 103.3 MB |
| `energy/weather/forecast` | 1 | 5,978 | `issued_at` | 2026-09-27T08:00Z | 2026-09-27T20:00Z | 665.0 KB |
| `energy/weather/observed` | 1 | 3,720 | `time` | 2026-09-24T00:00Z | 2026-09-27T20:00Z | 347.8 KB |

## Backfill progress

| Source | Range | Chunks done | Skipped (no data) | Remaining |
|---|---|---:|---:|---:|
| `aemo` | 1998-12-01 .. 2026-09-27 | 215 / 334 | 0 | 119 |
| `airquality` | 2022-08-01 .. 2026-09-27 | 117 / 200 | 0 | 83 |
| `eia` | 2015-07-01 .. 2026-09-27 | 10 / 135 | 42 | 83 |
| `eia_bulk` | 2015-07-01 .. 2026-09-27 | 7 / 7 | 0 | complete |
| `eia_market` | 1986-01-01 .. 2026-09-27 | 41 / 41 | 0 | complete |
| `era5` | 2015-01-01 .. 2026-09-27 | 480 / 480 | 0 | complete |
| `europe_power` | 2015-01-01 .. 2026-09-27 | 205 / 1410 | 0 | 1205 |
| `europe_price` | 2015-01-01 .. 2026-09-27 | 25 / 141 | 0 | 116 |
| `gb` | 2016-01-01 .. 2026-09-27 | 129 / 129 | 0 | complete |
| `nyiso_da` | 2000-01-01 .. 2026-09-27 | 321 / 321 | 0 | complete |
| `nyiso_rt` | 2000-01-01 .. 2026-09-27 | 321 / 321 | 0 | complete |
