"""Screening of hourly series, inspired by (and much simpler than) Ruggles et al. (2020), Scientific Data 7:155.

Each check marks suspicious points; flagged points become NaN, short gaps are interpolated, long gaps are kept
as NaN so the user decides how to handle them. The flag frame is returned so every change stays auditable.
"""
import numpy as np
import pandas as pd

CHECKS = ("nonpositive", "stuck", "level", "spike")


def screen(s, positive=True, low_level=True, stuck_hours=24, level_factor=10.0, spike_k=8.0, window=24 * 7):
    """Return (clean series, DataFrame of boolean flags per check).

    positive=False / low_level=False for series that can legitimately fall to or below zero, e.g. operational
    demand in regions with a lot of rooftop PV (AEMO SA1, VIC1 around midday).
    """
    s = pd.to_numeric(s, errors="coerce").astype(float)
    flags = pd.DataFrame(False, index=s.index, columns=CHECKS)

    if positive:
        flags["nonpositive"] = s <= 0

    # identical value repeated for many consecutive hours = frozen telemetry
    run_id = (s != s.shift()).cumsum()
    run_len = s.groupby(run_id).transform("size")
    flags["stuck"] = (run_len >= stuck_hours) & s.notna() & (s != 0)

    # implausible level vs. the monthly-scale rolling median
    med = s.rolling(window * 4, center=True, min_periods=24).median()
    ratio = s.abs() / med.abs()
    flags["level"] = (ratio > level_factor) | ((ratio < 1 / level_factor) & low_level)

    # isolated spikes: a jump away from BOTH neighbours (same sign) that is large relative to the typical
    # hour-to-hour change; a steep but monotone ramp is never flagged
    up, down = s - s.shift(1), s - s.shift(-1)
    step = s.diff().abs().rolling(window, center=True, min_periods=24).median() * 1.4826
    flags["spike"] = (np.sign(up) == np.sign(down)) & (np.minimum(up.abs(), down.abs()) > spike_k * step.replace(0, np.nan))

    flags = flags.fillna(False)
    clean = s.mask(flags.any(axis=1))
    return clean, flags


def fill_short_gaps(s, max_hours=3):
    """Linear interpolation of gaps up to `max_hours`; longer gaps stay NaN."""
    missing = s.isna()
    run_id = (missing != missing.shift()).cumsum()
    run_len = missing.groupby(run_id).transform("size")
    filled = s.interpolate(limit_area="inside")
    return filled.where(~missing | (run_len <= max_hours))


def longest_gap(s):
    missing = s.isna()
    return missing.groupby((~missing).cumsum()).sum().max() if len(s) else 0


def quality(raw, clean, flags):
    """One-line quality summary for a series."""
    n = len(raw)
    return {
        "hours": n,
        "missing_raw_%": round(100 * raw.isna().mean(), 2) if n else None,
        "longest_gap_h": int(longest_gap(raw)),
        **{f"flag_{c}": int(flags[c].sum()) for c in CHECKS},
        "missing_after_%": round(100 * clean.isna().mean(), 2) if n else None,
    }
