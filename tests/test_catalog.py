import importlib.util
import json
from pathlib import Path

import pandas as pd

from utils import backfill
from utils.storage import upsert


def load_catalog_module():
    path = Path(__file__).resolve().parent.parent / "scripts" / "build_catalog.py"
    spec = importlib.util.spec_from_file_location("build_catalog", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_catalog_lists_tables_progress_and_is_stable(data_dir):
    catalog = load_catalog_module()
    upsert(pd.DataFrame({"location": ["A", "A"], "time": ["2016-01-31T23:00Z", "2016-02-01T00:00Z"]}),
           "energy/weather/era5", ["location", "time"], "time")
    backfill.save_state("energy", {"era5": {"start": "2015-01-01", "end": "2026-09-27", "total": 10,
                                            "done": ["a", "b"], "skipped": ["c"]}})

    catalog.build("energy")
    text = (data_dir / "energy" / "CATALOG.md").read_text()
    assert "| `energy/weather/era5` | 2 | 2 | `time` | 2016-01-31T23:00Z | 2016-02-01T00:00Z |" in text
    assert "| `era5` | 2015-01-01 .. 2026-09-27 | 2 / 10 | 1 | 7 |" in text
    cache = json.loads((data_dir / "energy" / "_catalog_cache.json").read_text())
    assert set(cache) == {"energy/weather/era5/2016-01.csv.gz", "energy/weather/era5/2016-02.csv.gz"}

    catalog.build("energy")
    assert (data_dir / "energy" / "CATALOG.md").read_text() == text
