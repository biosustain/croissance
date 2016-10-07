import logging
from collections import namedtuple
from operator import attrgetter

import numpy
import pandas

from croissance.estimation.defaults import MINIMUM_VALID_OD, RESAMPLE_POINTS_PER_HOUR, MINIMUM_VALID_SLOPE, \
    MINIMUM_PHASE_LENGTH, PHASE_MIN_DELTA_LOG_OD, CURVE_MINIMUM_DURATION_HOURS
from croissance.estimation.outliers import remove_outliers
from croissance.estimation.ranking import rank_phases
from croissance.estimation.regression import fit_exponential
from croissance.estimation.smoothing import median_smoothing
from croissance.estimation.smoothing.segments import segment_spline_smoothing
from croissance.estimation.util import savitzky_golay, resample, with_overhangs, points_per_hour


class RawGrowthPhase(namedtuple('RawGrowthPhase', ('start', 'end'))):
    __slots__ = ()

    @property
    def duration(self):
        return self.end - self.start


class GrowthPhase(namedtuple('GrowthPhase', (
        'start',
        'end',
        'slope',
        'intercept',
        'n0',
        'attributes'
))):
    __slots__ = ()

    @property
    def duration(self):
        return self.end - self.start

    @classmethod
    def pick_best(cls, growth_phases, metric='duration'):
        try:
            return sorted(growth_phases, key=attrgetter(metric), reverse=True)[0]
        except IndexError:
            return None

    def __getattr__(self, item):
        return self.attributes.get(item, None)


AnnotatedGrowthCurve = namedtuple('AnnotatedGrowthCurve', ('series', 'outliers', 'growth_phases'))


class Estimator(object):
    def __init__(self,
                 *,
                 constrain_n0: bool = False,
                 n0: float = 0.0):
        self._logger = logging.getLogger(__name__)
        self._constrain_n0 = constrain_n0
        self._n0 = n0

    def _find_growth_phases(self, curve: 'pandas.Series', window) -> 'typing.List[RawGrowthPhase]':
        """
        Finds growth phases by locating regions in a series where both the first and second derivatives are positive.

        :param curve:
        :param window:
        :return:
        """
        first_derivative = savitzky_golay(curve, window, 3, deriv=1)
        second_derivative = savitzky_golay(curve, window, 3, deriv=2)

        growth = pandas.Series(index=curve.index,
                               data=(first_derivative.values > 0) & (second_derivative.values > 0))

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

    def growth(self, curve: pandas.Series) -> AnnotatedGrowthCurve:
        series = curve.dropna()

        n_hours = int(numpy.round(points_per_hour(series) * CURVE_MINIMUM_DURATION_HOURS))

        if n_hours % 2 == 0:
            n_hours += 1

        series, outliers = remove_outliers(series, window=n_hours, std=3)

        # NOTE workaround for issue with negative curves
        if len(series[series > 0]) < 3:
            return AnnotatedGrowthCurve(series, outliers, [])

        smooth_series = segment_spline_smoothing(series)

        phases = []
        raw_phases = self._find_growth_phases(smooth_series, window=n_hours)

        for phase in raw_phases:
            phase_series = series[phase.start:phase.end]

            # skip any growth phases that have not enough points for fitting
            if len(phase_series[phase_series > 0]) < 3:
                continue

            # skip any phases with less than minimum duration
            if phase.duration < defaults.PHASE_MINIMUM_DURATION_HOURS:
                continue

            # snr_estimate, slope_estimate = signal_noise_ratio_estimate(phase_series.values)
            # # skip any growth phase with <strike>an estimated S/N ratio < 1 or</strike> negative slope.
            # if slope_estimate <= 0:
            #     continue

            if self._constrain_n0:
                slope, intercept, n0, snr, fallback_linear_method = fit_exponential(phase_series, n0=self._n0)
            else:
                slope, intercept, n0, snr, fallback_linear_method = fit_exponential(phase_series)

            # skip phases whose actual slope is below the limit
            if slope < max(0.0, defaults.PHASE_MINIMUM_SLOPE):
                continue

            # skip phases whose actual signal-noise-ratio is below the limit
            if snr < max(1.0, defaults.PHASE_MINIMUM_SIGNAL_NOISE_RATIO):
                continue

            phases.append(GrowthPhase(phase.start, phase.end, slope, intercept, n0, {"SNR": snr}))

        ranked_phases = rank_phases(phases, defaults.PHASE_RANK_WEIGHTS, thresholds={
            'SNR': defaults.PHASE_MINIMUM_SIGNAL_NOISE_RATIO,
            'duration': defaults.PHASE_MINIMUM_DURATION_HOURS,
            'slope': defaults.PHASE_MINIMUM_SLOPE
        })

        return AnnotatedGrowthCurve(series, outliers, [phase for phase in ranked_phases
                                                       if phase.rank >= defaults.PHASE_RANK_EXCLUDE_BELOW])
