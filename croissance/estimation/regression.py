import numpy
from scipy.optimize import curve_fit
from scipy.stats import linregress


def exponential(x, a, b, c):
    return a * numpy.exp(b * x) + c


def fit_exponential(series, *, p0=(1.0, 0.01, 0.0), n0: float = None):
    """
    Fits an exponential to a series. First attempts an exponential fit in linear space
    using p0, then falls back to a fit in log space to attempt to find parameters p0
    for a linear fit; if all else fails returns the linear fit.
    """

    if n0 is None:
        fit_fn = exponential
    else:

        def exponential_constrain_n0(x, a, b):
            return a * numpy.exp(b * x) + n0

        fit_fn = exponential_constrain_n0
        p0 = p0[:2]

    try:
        popt, _pcov = curve_fit(
            fit_fn,
            series.index,
            series.values,
            p0=p0,
            maxfev=10000,
            bounds=([0.0, 0.0, 0.0], numpy.inf)
            if n0 is None
            else ([0.0, 0.0], numpy.inf),
        )

        if n0 is not None:
            popt = tuple(popt) + (n0,)
    except RuntimeError:
        pass
    else:
        slope = popt[1]
        intercept = numpy.log(1 / popt[0]) / slope
        N0 = popt[2]

        if slope >= 0:
            snr = signal_noise_ratio(series, *popt)
            return slope, intercept, N0, snr, False

    log_series = numpy.log(series[series > 0] - (n0 or 0.0))

    slope, c, *__ = linregress(log_series.index, log_series.values)
    intercept = -c / slope

    if n0 is None:
        p0 = (numpy.exp(c), slope, 0.0)
    else:
        p0 = (numpy.exp(c), slope)

    try:
        popt, _pcov = curve_fit(
            fit_fn,
            series.index,
            series.values,
            p0=p0,
            maxfev=10000,
            bounds=([0.0, 0.0, 0.0], numpy.inf)
            if n0 is None
            else ([0.0, 0.0], numpy.inf),
        )

        if n0 is not None:
            popt = tuple(popt) + (n0,)
    except RuntimeError:
        snr = signal_noise_ratio(series, c, slope, 0.0)
        return slope, intercept, (n0 or 0.0), snr, True
    else:
        slope = popt[1]
        intercept = numpy.log(1 / popt[0]) / slope
        n0 = popt[2]
        snr = signal_noise_ratio(series, *popt)
        return slope, intercept, n0, snr, False


def signal_noise_ratio(series, *popt):
    fit = exponential(series.index, *popt)
    return numpy.var(fit) / numpy.var(series.values - fit)
