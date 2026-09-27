# Data catalog: `energy`

Auto-generated after every collection run by `scripts/build_catalog.py`.

| Table | Files | Rows | Time column | From | To | Size |
|---|---:|---:|---|---|---|---:|
| `energy/airquality/observed` | 1 | 1,782 | `time` | 2026-09-24T00:00Z | 2026-09-27T08:00Z | 111.1 KB |
| `energy/weather/era5` | 97 | 1,541,976 | `time` | 2015-01-01T00:00Z | 2026-09-21T23:00Z | 36.9 MB |
| `energy/weather/forecast` | 1 | 858 | `issued_at` | 2026-09-27T08:00Z | 2026-09-27T08:00Z | 95.3 KB |
| `energy/weather/observed` | 1 | 1,782 | `time` | 2026-09-24T00:00Z | 2026-09-27T08:00Z | 165.2 KB |

## Backfill progress

| Source | Range | Chunks done | Skipped (no data) | Remaining |
|---|---|---:|---:|---:|
| `airquality` | 2022-08-01 .. 2026-09-27 | 0 / 110 | 0 | 110 |
| `era5` | 2015-01-01 .. 2026-09-27 | 175 / 264 | 0 | 89 |
