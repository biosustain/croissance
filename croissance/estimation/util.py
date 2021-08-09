import numpy
import pandas
from scipy.signal import savgol_filter


def points_per_hour(series):
    if len(series) < 2:
        return len(series)

    return 1 / numpy.median(series.index[1:] - series.index[:-1])


def savitzky_golay(series, *args, **kwargs):
    return pandas.Series(
        index=series.index, data=savgol_filter(series.values, *args, **kwargs)
    )


def with_overhangs(values, overhang_size):
    start_overhang = numpy.repeat(
        [numpy.median(values[0 : overhang_size // 2 + 1])], overhang_size
    )
    end_overhang = numpy.repeat(
        [numpy.max(values[-1 - overhang_size // 2 : -1])], overhang_size
    )
    return pandas.Series(numpy.concatenate([start_overhang, values, end_overhang]))


def normalize_time_unit(curve: pandas.Series, unit: str = "hours"):
    if unit == "hours":
        return curve
    elif unit == "minutes":
        return pandas.Series(index=curve.index / 60.0, data=curve.values)
    else:
        raise NotImplementedError("Unsupported time unit: '{}'".format(unit))
