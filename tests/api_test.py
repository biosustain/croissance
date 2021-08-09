from pathlib import Path

import matplotlib.pyplot as plt
import numpy
import pandas
import pytest


from pytest import approx

from croissance import process_curve, plot_processed_curve
from croissance.figures.writer import PDFWriter


def test_process_curve_empty_series():
    result = process_curve(pandas.Series([], dtype="float64"))

    assert result.series.empty
    assert result.outliers == []
    assert result.growth_phases == []


def test_process_curve_null_series():
    curve = pandas.Series(index=[1, 2], data=[None, float("NaN")])
    result = process_curve(curve)

    assert result.series is curve
    assert result.outliers == []
    assert result.growth_phases == []


def test_process_curve_time_unit():
    mu = 0.5
    pph = 4.0
    curve = pandas.Series(
        data=[numpy.exp(mu * i / pph) for i in range(100)],
        index=[i / pph for i in range(100)],
    )

    hours = process_curve(curve, unit="hours")
    minutes = process_curve(
        pandas.Series(index=curve.index * 60.0, data=curve.values),
        unit="minutes",
    )

    assert hours.series.equals(minutes.series)
    assert hours.outliers.equals(minutes.outliers)
    assert hours.growth_phases == minutes.growth_phases


def test_process_curve_basic():
    with PDFWriter(Path("test.basic.pdf")) as doc:
        mu = 0.5
        pph = 4.0
        curve = pandas.Series(
            data=[numpy.exp(mu * i / pph) for i in range(100)],
            index=[i / pph for i in range(100)],
        )

        result = process_curve(curve, constrain_n0=True, n0=0.0)

        # self.assertAlmostEqual(mu, slope, 6, msg='growth rate (mu)={}'.format(mu))

        doc.write("#0 n0=1", result)
        print(result.growth_phases)
        assert len(result.growth_phases) == 1
        assert mu == approx(result.growth_phases[0].slope, abs=1e-2)
        assert 0.0 == approx(result.growth_phases[0].n0, 1e-3)
        assert result.growth_phases[0].SNR > 1000

        result = process_curve(curve, constrain_n0=False)
        doc.write("#0 n0=auto", result)
        print(result.growth_phases)
        assert len(result.growth_phases) == 1
        assert mu == approx(result.growth_phases[0].slope, abs=1e-2)
        assert -0.25 < result.growth_phases[0].n0 < 0.25
        assert result.growth_phases[0].SNR > 1000

        curve = pandas.Series(
            data=(
                [1.0] * 5
                + [numpy.exp(mu * i / pph) for i in range(25)]
                + [numpy.exp(mu * 24 / pph)] * 20
            ),
            index=([i / pph for i in range(50)]),
        )

        result = process_curve(curve, constrain_n0=True, n0=0.0)
        doc.write("#1 n0=0", result)
        print(result.growth_phases)
        assert len(result.growth_phases) == 1
        assert mu == approx(result.growth_phases[0].slope, abs=1e-2)
        assert 0.0 == approx(result.growth_phases[0].n0, 1e-3)
        assert result.growth_phases[0].SNR > 1000

        result = process_curve(curve, constrain_n0=False)
        doc.write("#1 n0=auto", result)
        print(result.growth_phases)
        assert len(result.growth_phases) == 1
        assert mu == approx(result.growth_phases[0].slope, abs=1e-1)
        assert -0.25 < result.growth_phases[0].n0 < 0.25
        assert result.growth_phases[0].SNR > 1000

        mu = 0.20
        curve = pandas.Series(
            data=(
                [i / 10.0 for i in range(10)]
                + [numpy.exp(mu * i / pph) for i in range(25)]
                + [numpy.exp(mu * 24 / pph)] * 15
            ),
            index=([i / pph for i in range(50)]),
        )

        result = process_curve(curve, constrain_n0=True, n0=0.0)
        doc.write("#2 n0=0", result)
        print(result.growth_phases)
        assert len(result.growth_phases) == 1
        assert mu == approx(result.growth_phases[0].slope, abs=1e-2)
        assert 0.0 == approx(result.growth_phases[0].n0, 1e-6)
        assert result.growth_phases[0].SNR > 1000

        result = process_curve(curve, constrain_n0=False)
        doc.write("#2 n0=auto", result)
        assert len(result.growth_phases) == 1
        assert mu == approx(result.growth_phases[0].slope, abs=1e-2)
        assert -0.25 < result.growth_phases[0].n0 < 0.25
        assert result.growth_phases[0].SNR > 1000


def test_process_curve_wrong_time_unit():
    mu = 0.5
    pph = 0.1
    curve = pandas.Series(
        data=[numpy.exp(mu * i / pph) for i in range(100)],
        index=[i / pph for i in range(100)],
    )

    result = process_curve(curve, constrain_n0=False, n0=0.0)
    assert len(result.growth_phases) == 0
    assert list(result.series) == list(curve)


@pytest.mark.parametrize("yscale, naxis", (("linear", 1), ("log", 1), ("both", 2)))
def test_plot_processed_curve(yscale, naxis):
    mu = 0.5
    pph = 4.0
    curve = pandas.Series(
        data=[numpy.exp(mu * i / pph) for i in range(100)],
        index=[i / pph for i in range(100)],
    )

    curve = process_curve(curve, constrain_n0=True, n0=0.0)
    fig, axes = plot_processed_curve(curve, yscale=yscale)
    try:
        assert len(axes) == naxis
    finally:
        plt.close()
