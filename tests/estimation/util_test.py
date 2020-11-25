import pandas

from croissance.estimation.util import normalize_time_unit


def test_normalize_time_unit():
    curve = pandas.Series(index=[0, 15, 30, 60], data=[1, 2, 3, 4])

    assert pandas.Series(index=[0.0, 0.25, 0.5, 1.0], data=[1, 2, 3, 4]).equals(
        normalize_time_unit(curve, "minutes")
    )
