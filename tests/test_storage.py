import pandas as pd

from utils.storage import load_all, upsert


def test_upsert_partitions_by_month_and_replaces_revised_rows(data_dir):
    df = pd.DataFrame({"k": ["a", "b"], "t": ["2026-09-01T00:00Z", "2026-10-01T00:00Z"], "v": [1.0, None]})
    assert upsert(df, "x/y", ["k"], "t") == 2
    assert sorted(p.name for p in (data_dir / "x/y").iterdir()) == ["2026-09.csv", "2026-10.csv"]

    upsert(pd.DataFrame({"k": ["a"], "t": ["2026-09-01T00:00Z"], "v": [5.0]}), "x/y", ["k"], "t")
    got = load_all("x/y")
    assert len(got) == 2
    assert got.loc[got.k == "a", "v"].item() == "5.0"


def test_unchanged_gzip_partition_is_not_rewritten(data_dir):
    df = pd.DataFrame({"id": ["1"], "d": ["2026-09-22"], "txt": ["x"]})
    upsert(df, "p", ["id"], "d", ext=".csv.gz")
    path = data_dir / "p" / "2026-09.csv.gz"
    first = path.read_bytes()
    mtime = path.stat().st_mtime_ns
    upsert(df, "p", ["id"], "d", ext=".csv.gz")
    assert path.read_bytes() == first
    assert path.stat().st_mtime_ns == mtime


def test_new_columns_are_merged(data_dir):
    upsert(pd.DataFrame({"k": ["a"], "t": ["2026-09-01"]}), "z", ["k"], "t")
    upsert(pd.DataFrame({"k": ["b"], "t": ["2026-09-02"], "extra": ["e"]}), "z", ["k"], "t")
    got = load_all("z")
    assert list(got["extra"]) == ["", "e"]
