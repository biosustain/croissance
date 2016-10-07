import numpy
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

from croissance.estimation import AnnotatedGrowthCurve


class PDFWriter(object):
    def __init__(self, file, include_shifted_exponentials: bool = False):
        self.doc = PdfPages(file)
        self._include_shifted_exponentials = include_shifted_exponentials

    def write(self,
              name: str,
              curve: AnnotatedGrowthCurve):

        fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(16, 16))
        axes[1].set_yscale('log')

        try:
            plt.title(name)

            if curve.series.max() <= 0:
                return

            for axis in axes:
                axis.plot(curve.series.index,
                          curve.series.values,
                          color='black',
                          marker='.',
                          markersize=5,
                          linestyle='None')

                axis.plot(curve.outliers.index,
                          curve.outliers.values,
                          color='red',
                          marker='.',
                          markersize=5,
                          linestyle='None')

            colors = ['b', 'g', 'c', 'm', 'y', 'k']

            for i, phase in enumerate(curve.growth_phases):
                color = colors[i % len(colors)]

                # if phase['exclude'] is True:
                #     color = 'gray'

                a = 1 / numpy.exp(phase.intercept * phase.slope)

                def gf(x):
                    return a * numpy.exp(phase.slope * x) + phase.n0

                phase_series = curve.series[phase.start:phase.end]

                for axis in axes:
                    if self._include_shifted_exponentials:
                        axis.plot(phase_series.index,
                                  phase_series.values - phase.n0,
                                  marker='.', linewidth=0, color='red')

                        axis.plot(phase_series.index, gf(phase_series.index) - phase.n0,
                                  marker=None, linewidth=2, color='red')

                    axis.axhline(y=phase.n0, marker=None, linewidth=1, linestyle='dashed', color=color)
                    axis.axvline(x=phase.intercept, marker=None, linewidth=1, linestyle='dashed', color=color)

                    axis.plot(phase_series.index,
                              phase_series.values,
                              marker=None,
                              linewidth=15,
                              color=color,
                              solid_capstyle='round',
                              alpha=0.2)

                    axis.plot(curve.series.index, gf(curve.series.index), color=color, linewidth=1)
                    axis.plot(phase_series.index, gf(phase_series.index), color=color, linewidth=2)

            for axis in axes:
                axis.set_xlim(curve.series.index[0], curve.series.index[-1])

            axes[0].set_ylim([max(curve.series.min(), -2.5), curve.series.max()])
            axes[1].set_ylim([0.1, curve.series.max()])
        finally:
            self.doc.savefig(fig)
            plt.close()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def close(self):
        self.doc.close()
