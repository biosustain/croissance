import numpy
import pandas
import pytest

from croissance.estimation import fit_exponential


@pytest.mark.parametrize("mu", (0.001, 0.10, 0.15, 0.50, 1.0))
def test_regression_basic(mu):
    phase = numpy.exp(pandas.Series(range(20)) * mu)
    slope, intercept, n0, snr, lin = fit_exponential(phase)

    print(slope, intercept, n0, snr, lin)

    assert not lin, "This fit should not require a linear fallback."
    assert n0 == pytest.approx(0, abs=1e-3), "N0=0"
    assert intercept == pytest.approx(0, abs=1e-3), '"intercept"=0'
    assert mu == pytest.approx(slope, abs=1e-7), "growth rate (mu)={}".format(mu)
    assert snr > 100000, "signal-noise ratio should be very good"
