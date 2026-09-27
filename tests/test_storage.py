from datetime import date

import pandas as pd

from utils import storage
from utils.storage import compact, load_all, upsert


def recent_month(offset=0):
    t = pd.Timestamp.now().to_period("M") - offset
    return str(t)


def test_upsert_partitions_by_month_and_replaces_revised_rows(data_dir):
    m0, m1 = recent_month(1), recent_month(0)
    df = pd.DataFrame({"k": ["a", "b"], "t": [f"{m0}-01T00:00Z", f"{m1}-01T00:00Z"], "v": [1.0, None]})
    assert upsert(df, "x/y", ["k"], "t") == 2
    assert sorted(p.name for p in (data_dir / "x/y").iterdir()) == [f"{m0}.csv", f"{m1}.csv"]

    upsert(pd.DataFrame({"k": ["a"], "t": [f"{m0}-01T00:00Z"], "v": [5.0]}), "x/y", ["k"], "t")
    got = load_all("x/y")
    assert len(got) == 2
    assert got.loc[got.k == "a", "v"].item() == "5.0"


def test_cold_months_are_gzipped_and_hot_months_plain():
    today = date(2026, 9, 27)
    assert not storage.is_cold("2026-09", today)
    assert not storage.is_cold("2026-07", today)
    assert storage.is_cold("2026-06", today)
    assert storage.is_cold("2015-01", today)


def test_unchanged_gzip_partition_is_not_rewritten(data_dir):
    df = pd.DataFrame({"id": ["1"], "d": ["2016-09-22"], "txt": ["x"]})
    upsert(df, "p", ["id"], "d")
    path = data_dir / "p" / "2016-09.csv.gz"
    first = path.read_bytes()
    mtime = path.stat().st_mtime_ns
    upsert(df, "p", ["id"], "d")
    assert path.read_bytes() == first
    assert path.stat().st_mtime_ns == mtime


def test_compact_moves_cold_csv_to_gz_and_upsert_merges_both(data_dir):
    (data_dir / "e" / "t").mkdir(parents=True)
    pd.DataFrame({"k": ["a"], "t": ["2016-01-01"]}).to_csv(data_dir / "e/t/2016-01.csv", index=False)
    assert compact("e") == 1
    assert [p.name for p in (data_dir / "e/t").iterdir()] == ["2016-01.csv.gz"]
    upsert(pd.DataFrame({"k": ["b"], "t": ["2016-01-02"]}), "e/t", ["k"], "t")
    assert sorted(load_all("e/t").k) == ["a", "b"]


def test_new_columns_are_merged(data_dir):
    upsert(pd.DataFrame({"k": ["a"], "t": ["2026-09-01"]}), "z", ["k"], "t")
    upsert(pd.DataFrame({"k": ["b"], "t": ["2026-09-02"], "extra": ["e"]}), "z", ["k"], "t")
    got = load_all("z")
    assert list(got["extra"]) == ["", "e"]
