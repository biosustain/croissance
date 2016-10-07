from croissance.estimation import Estimator


def process_curve(curve: 'pandas.Series', **kwargs):
    estimator = Estimator(**kwargs)
    return estimator.growth(curve)




