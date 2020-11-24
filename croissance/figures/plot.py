import matplotlib.pyplot as plt
import numpy

from croissance.estimation import AnnotatedGrowthCurve


def plot_processed_curve(curve: AnnotatedGrowthCurve, name: str, yscale="log"):
    fig, axes = plt.subplots(nrows=2 if yscale == "both" else 1, ncols=1)
    fig.suptitle(name)

    if curve.series.max() <= 0:
        return

    if yscale == "both":
        _do_plot_processed_curve(curve, axes[0], "linear")
        _do_plot_processed_curve(curve, axes[1], "log")

        return fig, axes
    elif yscale in ("log", "linear"):
        _do_plot_processed_curve(curve, axes, yscale)

        return fig, [axes]
    else:
        raise ValueError(yscale)


def _do_plot_processed_curve(curve, axis, yscale):
    axis.plot(
        curve.series.index,
        curve.series.values,
        color="black",
        marker=".",
        markersize=5,
        linestyle="None",
    )

    axis.plot(
        curve.outliers.index,
        curve.outliers.values,
        color="red",
        marker=".",
        markersize=5,
        linestyle="None",
    )

    colors = ["b", "g", "c", "m", "y", "k"]

    for i, phase in enumerate(curve.growth_phases):
        color = colors[i % len(colors)]

        a = 1 / numpy.exp(phase.intercept * phase.slope)

        def gf(x):
            return a * numpy.exp(phase.slope * x) + phase.n0

        phase_series = curve.series[phase.start : phase.end]

        axis.axhline(
            y=phase.n0,
            marker=None,
            linewidth=1,
            linestyle="dashed",
            color=color,
        )
        axis.axvline(
            x=phase.intercept,
            marker=None,
            linewidth=1,
            linestyle="dashed",
            color=color,
        )

        axis.axhline(y=phase.n0, linewidth=1, linestyle="dashed", color=color)
        axis.axvline(x=phase.intercept, linewidth=1, linestyle="dashed", color=color)

        axis.plot(
            phase_series.index,
            phase_series.values,
            marker=None,
            linewidth=15,
            color=color,
            solid_capstyle="round",
            alpha=0.2,
        )

        axis.plot(curve.series.index, gf(curve.series.index), color=color, linewidth=1)
        axis.plot(phase_series.index, gf(phase_series.index), color=color, linewidth=2)

    yvalues = curve.series
    ymargin = (yvalues.max() - yvalues.min()) * 0.025
    yvalues_min = 0.01 if yscale == "log" else float("-inf")
    axis.set_ylim([max(yvalues.min() - ymargin, yvalues_min), yvalues.max() + ymargin])

    xvalues = curve.series.index
    xmargin = (xvalues.max() - xvalues.min()) * 0.025
    axis.set_xlim([xvalues.min() - xmargin, xvalues.max() + xmargin])

    axis.set_yscale(yscale)
