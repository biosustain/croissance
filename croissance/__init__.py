from croissance.estimation import Estimator


def process_curve(curve: 'pandas.Series', **kwargs):
    estimator = Estimator(**kwargs)
    if curve.empty:
        return None
    return estimator.growth(curve)




