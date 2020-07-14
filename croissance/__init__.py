from croissance.estimation import Estimator
from collections import namedtuple

AnnotatedGrowthCurve = namedtuple('AnnotatedGrowthCurve', ('series', 'outliers', 'growth_phases'))


def process_curve(curve: 'pandas.Series', **kwargs):
    estimator = Estimator(**kwargs)
    if curve.isnull().all():
        return AnnotatedGrowthCurve(curve, [], [])
    return estimator.growth(curve)




