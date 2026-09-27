import importlib.util
from pathlib import Path

import pandas as pd

from utils.storage import upsert


def load_catalog_module():
    path = Path(__file__).resolve().parent.parent / "scripts" / "build_catalog.py"
    spec = importlib.util.spec_from_file_location("build_catalog", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_catalog_lists_tables_and_is_stable(data_dir, monkeypatch):
    catalog = load_catalog_module()
    monkeypatch.setattr(catalog, "DATA_DIR", data_dir)
    upsert(pd.DataFrame({"location": ["A", "A"], "time": ["2026-08-31T23:00Z", "2026-09-01T00:00Z"]}),
           "energy/weather/observed", ["location", "time"], "time")

    catalog.build("energy")
    text = (data_dir / "energy" / "CATALOG.md").read_text()
    assert "| `energy/weather/observed` | 2 | 2 | `time` | 2026-08-31T23:00Z | 2026-09-01T00:00Z |" in text
    catalog.build("energy")
    assert (data_dir / "energy" / "CATALOG.md").read_text() == text
