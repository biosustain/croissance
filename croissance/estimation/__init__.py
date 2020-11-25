import logging

from collections import namedtuple
from operator import attrgetter

import numpy
import pandas

import croissance.estimation.defaults as defaults

from croissance.estimation.outliers import remove_outliers
from croissance.estimation.ranking import rank_phases
from croissance.estimation.regression import fit_exponential
from croissance.estimation.smoothing.segments import segment_spline_smoothing
from croissance.estimation.util import savitzky_golay, points_per_hour


class RawGrowthPhase(namedtuple("RawGrowthPhase", ("start", "end"))):
    __slots__ = ()

    @property
    def duration(self):
        return self.end - self.start


class GrowthPhase(
    namedtuple(
        "GrowthPhase", ("start", "end", "slope", "intercept", "n0", "SNR", "rank")
    )
):
    __slots__ = ()

    @property
    def duration(self):
        return self.end - self.start

    @staticmethod
    def pick_best(growth_phases, metric="duration"):
        growth_phases = sorted(growth_phases, key=attrgetter(metric))
        if growth_phases:
            return growth_phases[-1]

        return None


AnnotatedGrowthCurve = namedtuple(
    "AnnotatedGrowthCurve", ("series", "outliers", "growth_phases")
)


def estimate_growth(
    curve: pandas.Series,
    *,
    segment_log_n0: bool = False,
    constrain_n0: bool = False,
    n0: float = 0.0,
    name: str = "untitled curve"
) -> AnnotatedGrowthCurve:
    log = logging.getLogger(__name__)
    series = curve.dropna()

    n_hours = int(
        numpy.round(points_per_hour(series) * defaults.CURVE_MINIMUM_DURATION_HOURS)
    )

    if n_hours == 0:
        log.warning(
            "Fewer than one data-point per hour for %s. Use the command-line "
            "`--input-time-unit minutes` if times are represented in minutes.",
            name,
        )
        return AnnotatedGrowthCurve(series, pandas.Series(dtype="float64"), [])

    if n_hours % 2 == 0:
        n_hours += 1

    series, outliers = remove_outliers(series, window=n_hours, std=3)

    # NOTE workaround for issue with negative curves
    if len(series[series > 0]) < 3:
        log.warning("Fewer than three positive data-points for %s", name)
        return AnnotatedGrowthCurve(series, outliers, [])

    if segment_log_n0:
        series_log_n0 = numpy.log(series - n0).dropna()
        smooth_series = segment_spline_smoothing(series, series_log_n0)
    else:
        smooth_series = segment_spline_smoothing(series)

    if len(smooth_series) < n_hours:
        log.warning("Insufficient smoothed data for %s", name)
        return AnnotatedGrowthCurve(series, outliers, [])

    phases = []
    for phase in _find_growth_phases(smooth_series, window=n_hours):
        phase_series = series[phase.start : phase.end]

        # skip any growth phases that have not enough points for fitting
        if len(phase_series[phase_series > 0]) < 3:
            continue

        # skip any phases with less than minimum duration
        if phase.duration < defaults.PHASE_MINIMUM_DURATION_HOURS:
            continue

        slope, intercept, n0, snr, _fallback_linear_method = fit_exponential(
            phase_series, n0=n0 if constrain_n0 else None
        )

        # skip phases whose actual slope is below the limit
        if slope < max(0.0, defaults.PHASE_MINIMUM_SLOPE):
            continue

        # skip phases whose actual signal-noise-ratio is below the limit
        if snr < max(1.0, defaults.PHASE_MINIMUM_SIGNAL_NOISE_RATIO):
            continue

        phases.append(
            GrowthPhase(
                start=phase.start,
                end=phase.end,
                slope=slope,
                intercept=intercept,
                n0=n0,
                SNR=snr,
                rank=None,
            )
        )

    ranked_phases = rank_phases(
        phases,
        defaults.PHASE_RANK_WEIGHTS,
        thresholds={
            "SNR": defaults.PHASE_MINIMUM_SIGNAL_NOISE_RATIO,
            "duration": defaults.PHASE_MINIMUM_DURATION_HOURS,
            "slope": defaults.PHASE_MINIMUM_SLOPE,
        },
    )

    return AnnotatedGrowthCurve(
        series,
        outliers,
        [
            phase
            for phase in ranked_phases
            if phase.rank >= defaults.PHASE_RANK_EXCLUDE_BELOW
        ],
    )


def _find_growth_phases(curve: "pandas.Series", window):
    """
    Finds growth phases by locating regions in a series where both the first and
    second derivatives are positive.
    """
    first_derivative = savitzky_golay(curve, window, 3, deriv=1)
    second_derivative = savitzky_golay(curve, window, 3, deriv=2)

    growth = pandas.Series(
        index=curve.index,
        data=(first_derivative.values > 0) & (second_derivative.values > 0),
    )

    istart, iend, phases = None, None, []
    for i, v in zip(growth.index, growth.values):
        if v:
            if istart is None:
                istart = i
        elif istart is not None:
            phases.append(RawGrowthPhase(istart, iend))
            istart = None
        iend = i

    if istart is not None:
        phases.append(RawGrowthPhase(istart, iend))

    return phases
