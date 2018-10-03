from croissance.estimation import Estimator


def process_curve(curve: 'pandas.Series', **kwargs):
    estimator = Estimator(**kwargs)
    if curve.isnull().all():
        return AnnotatedGrowthCurve(curve, [], [])
    return estimator.growth(curve)




