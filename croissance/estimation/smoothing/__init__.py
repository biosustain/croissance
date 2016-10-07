import pandas

from croissance.estimation.util import with_overhangs


def median_smoothing(series, window=10):
    data = pandas.rolling_apply(with_overhangs(series.values, window // 2),
                                window,
                                median_window_clean,
                                center=True)[window // 2:-window // 2]
    return pandas.Series(index=series.index, data=data)
