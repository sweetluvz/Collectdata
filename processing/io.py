"""Read raw monthly partitions into time-indexed frames.

Time convention of every processed output: UTC, hourly, labelled by the END of the hour
(`2020-01-01T01:00Z` = 00:00-01:00 UTC). Raw conventions differ per source:
  interval END   : EIA (`period`), AEMO, Open-Meteo radiation (mean of the preceding hour)
  interval START : Energy-Charts, Elexon, Carbon Intensity, NYISO
  instant        : Open-Meteo temperature, wind, humidity, pressure (value at the timestamp)
"""
from pathlib import Path
import re

import pandas as pd

from utils import storage

END, START = "end", "start"


def _months(start, end):
    if start is None or end is None:
        return None
    return {str(p) for p in pd.period_range(pd.Timestamp(start).to_period("M") - 1, pd.Timestamp(end).to_period("M") + 1)}


def load(table, time_col, start=None, end=None, columns=None, where=None):
    """Concatenate data/<table>/YYYY-MM.csv[.gz] (only the months needed) with a UTC DatetimeIndex.

    where=(column, allowed values) filters rows file by file, so large tables never sit in memory whole.
    """
    wanted = _months(start, end)
    files = [f for f in storage.data_files(storage.DATA_DIR / table)
             if wanted is None or re.match(r"\d{4}-\d{2}", f.name) and f.name[:7] in wanted]
    if not files:
        return pd.DataFrame()
    keep = None if columns is None else {time_col, *columns, *([where[0]] if where else [])}
    usecols = None if keep is None else (lambda c: c in keep)
    parts = []
    for f in files:
        part = pd.read_csv(f, usecols=usecols, low_memory=False)
        if where is not None:
            part = part[part[where[0]].isin(where[1])]
        parts.append(part)
    df = pd.concat(parts, ignore_index=True)
    if df.empty:
        return df
    df.index = pd.to_datetime(df.pop(time_col), utc=True, format="mixed")
    df = df.sort_index()
    if start is not None:
        df = df[df.index >= pd.Timestamp(start, tz="UTC")]
    if end is not None:
        df = df[df.index <= pd.Timestamp(end, tz="UTC")]
    return df


def to_hourly_end(df, stamps, how="mean"):
    """Resample to hourly, labelled at the end of the hour.

    stamps=START: a row at t covers [t, t+step)  -> bucket [H, H+1h) labelled H+1h
    stamps=END  : a row at t covers (t-step, t]  -> bucket (H, H+1h] labelled H+1h
    """
    closed = "left" if stamps == START else "right"
    numeric = df.apply(pd.to_numeric, errors="coerce")
    return getattr(numeric.resample("1h", closed=closed, label="right"), how)()


def output_dir():
    path = Path(storage.DATA_DIR).parent / "processed"
    path.mkdir(parents=True, exist_ok=True)
    return path
