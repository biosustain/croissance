import pandas

from croissance.estimation.util import with_overhangs


def remove_outliers(series, window=30, std=2):
    """
    Removes any points where the distance of the median exceeds ``std`` standard deviations within a rolling window.

    :param series:
    :param window:
    :param std:
    :return:
    """
    if len(series.values) < 10:
        return series, pandas.Series(data=[], index=[])

    values = with_overhangs(series.values, window)
    outliers = abs(values - pandas.rolling_median(values, window=window, center=True)) < pandas.rolling_std(values,
                                                                                                            window=window,
                                                                                                            center=True) * std
    outlier_mask = outliers[window:-window]

    outliers = pandas.Series(data=series.values[~outlier_mask], index=series.index[~outlier_mask])
    series = pandas.Series(data=series.values[outlier_mask], index=series.index[outlier_mask])

    return series, outliers