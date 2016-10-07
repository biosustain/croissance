import numpy
import pandas
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.signal import savgol_filter


def points_per_hour(series):
    return 1 / numpy.median([series.index[i] - series.index[i - 1] for i in range(1, len(series))])


def resample(series, *, factor=10, size=None):
    """
    Returns a new series re-sampled to a given number of points.

    :param series:
    :param factor: a number of points per unit time to scale the series to.
    :param size: a number of points to scale the series to.
    :return:
    """
    series = series.dropna()
    start, end = series.index[0], series.index[-1]

    if size is None:
        size = (end - start) * factor

    index = numpy.linspace(start, end, size)
    spline = InterpolatedUnivariateSpline(series.index, series.values)
    return pandas.Series(index=index, data=spline(index))


def savitzky_golay(series, *args, **kwargs):
    return pandas.Series(index=series.index, data=savgol_filter(series.values, *args, **kwargs))


def with_overhangs(values, overhang_size):
    start_overhang = numpy.repeat([numpy.median(values[0:overhang_size // 2 + 1])], overhang_size)
    end_overhang = numpy.repeat([numpy.max(values[-1 - overhang_size // 2:-1])], overhang_size)
    return numpy.concatenate([start_overhang, values, end_overhang])