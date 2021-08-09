import logging

from collections import namedtuple
from operator import attrgetter

import numpy
import pandas

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


class GrowthEstimationParameters:
    __slots__ = [
        "segment_log_n0",
        "constrain_n0",
        "n0",
        "curve_minimum_duration_hours",
        "phase_minimum_signal_noise_ratio",
        "phase_minimum_duration_hours",
        "phase_minimum_slope",
        "phase_rank_exclude_below",
        "phase_rank_weights",
    ]

    def __init__(self):
        self.segment_log_n0 = False
        self.constrain_n0 = False
        self.n0 = 0.0

        self.curve_minimum_duration_hours = 5
        self.phase_minimum_signal_noise_ratio = 1.0
        self.phase_minimum_duration_hours = 1.5
        self.phase_minimum_slope = 0.005

        self.phase_rank_exclude_below = 33
        self.phase_rank_weights = {
            "SNR": 50,
            "duration": 30,
            "slope": 10,
            # TODO add 1 - start?
        }


def estimate_growth(
    curve: pandas.Series,
    *,
    params=GrowthEstimationParameters(),
    name: str = "untitled curve"
) -> AnnotatedGrowthCurve:
    log = logging.getLogger(__name__)
    series = curve.dropna()

    n_hours = int(
        numpy.round(
            points_per_hour(series) * max(1, params.curve_minimum_duration_hours)
        )
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

    if params.segment_log_n0:
        series_log_n0 = numpy.log(series - params.n0).dropna()
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
        if phase.duration < max(0.0, params.phase_minimum_duration_hours):
            continue

        slope, intercept, n0, snr, _fallback_linear_method = fit_exponential(
            phase_series, n0=params.n0 if params.constrain_n0 else None
        )

        # skip phases whose actual slope is below the limit
        if slope < max(0.0, params.phase_minimum_slope):
            continue

        # skip phases whose actual signal-noise-ratio is below the limit
        if snr < max(1.0, params.phase_minimum_signal_noise_ratio):
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
        params.phase_rank_weights,
        thresholds={
            "duration": max(0.0, params.phase_minimum_duration_hours),
            "slope": max(0.0, params.phase_minimum_slope),
            "SNR": max(1.0, params.phase_minimum_signal_noise_ratio),
        },
    )

    return AnnotatedGrowthCurve(
        series,
        outliers,
        [
            phase
            for phase in ranked_phases
            if phase.rank >= params.phase_rank_exclude_below
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
