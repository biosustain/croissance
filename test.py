from unittest import TestCase

import numpy
import pandas

from croissance import process_curve
from croissance.estimation import fit_exponential
from croissance.estimation.util import normalize_time_unit
from croissance.figures import PDFWriter


class CroissanceTestCase(TestCase):
    def test_regression_basic(self):
        for mu in (0.001, 0.10, 0.15, 0.50, 1.0):
            phase = pandas.Series(
                data=[numpy.exp(i * mu) for i in range(20)],
                index=[i for i in range(20)],
            )

            slope, intercept, n0, snr, lin = fit_exponential(phase)
            print(slope, intercept, n0, snr, lin)

            self.assertFalse(lin, "This fit should not require a linear fallback.")
            self.assertAlmostEqual(n0, 0, 2, msg="N0=0")
            self.assertAlmostEqual(intercept, 0, 2, msg='"intercept"=0')
            self.assertAlmostEqual(mu, slope, 6, msg="growth rate (mu)={}".format(mu))
            self.assertTrue(snr > 100000, "signal-noise ratio should be very good")

    def test_process_curve_basic(self):
        with open("./test.basic.pdf", "wb") as f:
            with PDFWriter(f) as doc:
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
                self.assertEqual(len(result.growth_phases), 1)
                self.assertAlmostEqual(mu, result.growth_phases[0].slope, 2)
                self.assertAlmostEqual(0.0, result.growth_phases[0].n0, 3)
                self.assertTrue(result.growth_phases[0].SNR > 1000)

                result = process_curve(curve, constrain_n0=False)
                doc.write("#0 n0=auto", result)
                print(result.growth_phases)
                self.assertEqual(len(result.growth_phases), 1)
                self.assertAlmostEqual(mu, result.growth_phases[0].slope, 2)
                self.assertTrue(-0.25 < result.growth_phases[0].n0 < 0.25)
                self.assertTrue(result.growth_phases[0].SNR > 1000)

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
                self.assertEqual(len(result.growth_phases), 1)
                self.assertAlmostEqual(mu, result.growth_phases[0].slope, 2)
                self.assertAlmostEqual(0.0, result.growth_phases[0].n0, 3)
                self.assertTrue(result.growth_phases[0].SNR > 1000)

                result = process_curve(curve, constrain_n0=False)
                doc.write("#1 n0=auto", result)
                print(result.growth_phases)
                self.assertEqual(len(result.growth_phases), 1)
                self.assertAlmostEqual(mu, result.growth_phases[0].slope, 1)
                self.assertTrue(-0.25 < result.growth_phases[0].n0 < 0.25)
                self.assertTrue(result.growth_phases[0].SNR > 1000)

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
                self.assertEqual(len(result.growth_phases), 1)
                self.assertAlmostEqual(mu, result.growth_phases[0].slope, 2)
                self.assertAlmostEqual(0.0, result.growth_phases[0].n0, 6)
                self.assertTrue(result.growth_phases[0].SNR > 1000)

                result = process_curve(curve, constrain_n0=False)
                doc.write("#2 n0=auto", result)
                self.assertEqual(len(result.growth_phases), 1)
                self.assertAlmostEqual(mu, result.growth_phases[0].slope, 2)
                self.assertTrue(-0.25 < result.growth_phases[0].n0 < 0.25)
                self.assertTrue(result.growth_phases[0].SNR > 1000)

    def test_process_curve_wrong_time_unit(self):
        mu = 0.5
        pph = 0.1
        curve = pandas.Series(
            data=[numpy.exp(mu * i / pph) for i in range(100)],
            index=[i / pph for i in range(100)],
        )

        result = process_curve(curve, constrain_n0=False, n0=0.0)
        self.assertEqual(len(result.growth_phases), 0)
        self.assertEqual(list(result.series), list(curve))

    def test_normalize_time_unit(self):
        curve = pandas.Series(index=[0, 15, 30, 60], data=[1, 2, 3, 4])
        self.assertTrue(
            pandas.Series(index=[0.0, 0.25, 0.5, 1.0], data=[1, 2, 3, 4]).equals(
                normalize_time_unit(curve, "minutes")
            )
        )
