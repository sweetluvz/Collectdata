# Data catalog: `energy`

Auto-generated after every collection run by `scripts/build_catalog.py`.

| Table | Files | Rows | Time column | From | To | Size |
|---|---:|---:|---|---|---|---:|
| `energy/airquality/observed` | 1 | 3,320 | `time` | 2026-09-24T00:00Z | 2026-09-27T10:00Z | 208.1 KB |
| `energy/weather/era5` | 97 | 2,425,128 | `time` | 2015-01-01T00:00Z | 2026-09-21T23:00Z | 58.7 MB |
| `energy/weather/forecast` | 1 | 2,338 | `issued_at` | 2026-09-27T08:00Z | 2026-09-27T10:00Z | 260.1 KB |
| `energy/weather/observed` | 1 | 3,320 | `time` | 2026-09-24T00:00Z | 2026-09-27T10:00Z | 310.3 KB |

## Backfill progress

| Source | Range | Chunks done | Skipped (no data) | Remaining |
|---|---|---:|---:|---:|
| `airquality` | 2022-08-01 .. 2026-09-27 | 0 / 200 | 0 | 200 |
| `eia` | 2015-07-01 .. 2026-09-27 | 0 / 0 | 0 | waiting (API key missing?) |
| `eia_market` | 1986-01-01 .. 2026-09-27 | 0 / 0 | 0 | waiting (API key missing?) |
| `era5` | 2015-01-01 .. 2026-09-27 | 275 / 480 | 0 | 205 |
