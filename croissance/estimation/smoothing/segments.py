import numpy
import pandas

from scipy.signal import detrend
from scipy.interpolate import InterpolatedUnivariateSpline


def segment_by_std_dev(series, increment=2, maximum=20):
    """
    Divides a series into segments, minimizing standard deviation over window size.
    Windows are of varying size from `increment` to `maximum * increment` at each
    offset `increment` within the series.
    """
    start = int(series.index.min())
    duration = int(series.index[-2])

    windows = []
    for i in range(start, duration, increment):
        for size in range(1, maximum + 1):
            window = series[i : i + size * increment]
            # Gaps in measurements may result in empty windows
            if not window.empty:
                window = detrend(window)
                windows.append(
                    (window.std() / (size * increment), i, i + size * increment)
                )

    segments = []
    spots = set()
    for _window_agv_std, start, end in sorted(windows):
        window_spots = range(start, int(end))

        if not any(i in spots for i in window_spots):
            segments.append((start, min(duration, end)))
            spots.update(window_spots)

    return sorted(segments)


def window_median(window, start, end):
    x = numpy.linspace(0, 1, num=len(window))
    A = numpy.vstack([x, numpy.ones(len(x))]).T
    m, _c = numpy.linalg.lstsq(A, window, rcond=None)[0]

    return (start + end) / 2, m * 0.5 + numpy.median(window - m * x)


def segment_points(series, segments):
    """
    Picks knot points for an interpolating spline along a series of segments according
    to these rules:

    - For small segments, add a knot in the center of the segment
    - For medium-sized segments, add a knot near the beginning and end of the segment
    - For large segments, add a knot a knot near the beginning and end of the segment,
      and one in the center.
    """
    out = [(series.index[0], numpy.median(series[: series.index[0] + 1]))]

    def _add_knot(start, end):
        window = series[start:end]
        if not window.empty:
            out.append(window_median(window, start, end))

    for start, end in segments:
        if end - start > 5:
            _add_knot(start, start + 2)

            if end - start > 11:
                _add_knot(start + 2, end - 2)

            _add_knot(end - 2, end)
        else:
            _add_knot(start, end)

    out += [(series.index[-1], numpy.max(series[series.index[0] - 1 :]))]

    index, data = zip(*out)
    return pandas.Series(index=index, data=data)


def segment_spline_smoothing(series, series_std_dev=None, k=3):
    if series_std_dev is None:
        series_std_dev = series

    segments = segment_by_std_dev(series_std_dev)
    points = segment_points(series, segments).sort_index()
    if len(points) < k + 1:
        # InterpolatedUnivariateSpline requires at k + 1 points
        return pandas.Series(dtype="float64")

    spline = InterpolatedUnivariateSpline(points.index, points.values, k=k)
    return pandas.Series(data=spline(series.index), index=series.index)
