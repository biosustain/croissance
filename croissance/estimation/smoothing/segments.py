from heapq import heappush, heappop

import numpy
import pandas
from scipy.signal import detrend
from scipy.interpolate import InterpolatedUnivariateSpline


def segment_by_std_dev(series, increment=2, maximum=20):
    """
    Divides a series into segments, minimizing standard deviation over window size. Windows are of varying size from
    `increment` to `maximum * increment` at each offset `increment` within the series.

    :param series:
    :param increment:
    :param maximum:
    :return:
    """
    duration = int(series.index[-1])
    windows = []

    for i in range(0, duration, increment):
        for size in range(1, maximum + 1):
            window = detrend(series[i:i + size*increment])
            heappush(windows, (window.std() / (size*increment), i, i + size*increment))

    segments = []
    spots = set()

    try:
        while True:
            window_agv_std, start, end = heappop(windows)

            if any(i in spots for i in range(start, int(end))):
                continue

            for i in range(start, int(end)):
                spots.add(int(i))

            heappush(segments, (start, min(duration, end)))

    except IndexError:
        pass

    return [heappop(segments) for _ in range(len(segments))]


def window_median(window, start, end):
    x = numpy.linspace(0, 1, num=len(window))
    A = numpy.vstack([x, numpy.ones(len(x))]).T
    m, c = numpy.linalg.lstsq(A, window)[0]

    return (start + end) / 2, m * 0.5 + numpy.median(window - m * x)


def segment_points(series, segments):
    """
    Picks knot points for an interpolating spline along a series of segments according to these rules:

    - For small segments, add a knot in the center of the segment
    - For medium-sized segments, add a knot each near the beginning and end of the segment
    - For large segments, add a knot a knot each near the beginning and end of the segment, and one in the center.

    :param series:
    :param segments:
    :return:
    """
    out = [(series.index[0], numpy.median(series[:series.index[0] + 1]))]

    for start, end in segments:
        window = series[start:end]

        if end - start > 5:
            out.append(window_median(series[start:start + 2], start, start + 2))

            if end - start > 11:
                out.append(window_median(series[start + 2:end - 2], start + 2, end - 2))

            out.append(window_median(series[end - 2:end], end - 2, end))
        else:
            out.append(window_median(window, start, end))

    out += [(series.index[-1], numpy.max(series[series.index[0] - 1:]))]

    index, data = zip(*out)
    return pandas.Series(index=index, data=data)


def segment_spline_smoothing(series):
    segments = segment_by_std_dev(series)
    points = segment_points(series, segments)
    spline = InterpolatedUnivariateSpline(points.index, points.values, k=3)
    return pandas.Series(data=spline(series.index), index=series.index)
