from collections import namedtuple

from croissance.estimation import Estimator
from croissance.estimation.util import normalize_time_unit


AnnotatedGrowthCurve = namedtuple(
    "AnnotatedGrowthCurve", ("series", "outliers", "growth_phases")
)


def process_curve(
    curve: "pandas.Series",
    segment_log_n0: bool = False,
    constrain_n0: bool = False,
    n0: float = 0.0,
    unit: str = "hours",
):
    curve = normalize_time_unit(curve, unit)
    if curve.isnull().all():
        return AnnotatedGrowthCurve(curve, [], [])

    return Estimator(
        segment_log_n0=segment_log_n0,
        constrain_n0=constrain_n0,
        n0=n0,
    ).growth(curve)
