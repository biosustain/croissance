import pandas

from croissance.estimation.util import with_overhangs


def remove_outliers(series, window=30, std=2):
    """
    Returns a tuple containing a series with points removed where the distance of the
    median exceeds ``std`` standard deviations within a rolling window, and a series
    containing the removed outliers.
    """
    if len(series.values) < 10:
        return series, pandas.Series([], dtype="float64")

    values = with_overhangs(series.values, window)
    windows = values.rolling(window=window, center=True)
    outliers = abs(values - windows.median()) >= windows.std() * std
    outlier_mask = outliers[window:-window].values

    return series[~outlier_mask], series[outlier_mask]
