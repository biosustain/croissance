import pandas

import croissance.figures.plot

from croissance.estimation import AnnotatedGrowthCurve, estimate_growth
from croissance.estimation.util import normalize_time_unit


__all__ = [
    "plot_processed_curve",
    "process_curve",
]


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

    return estimate_growth(
        curve,
        segment_log_n0=segment_log_n0,
        constrain_n0=constrain_n0,
        n0=n0,
    )


def plot_processed_curve(curve: AnnotatedGrowthCurve, yscale="both"):
    return croissance.figures.plot.plot_processed_curve(curve=curve, yscale=yscale)
