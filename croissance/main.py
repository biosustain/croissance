#!/usr/bin/env python
import argparse
import logging
import sys

from pathlib import Path

import coloredlogs

from croissance import Estimator
from croissance.estimation.util import normalize_time_unit
from croissance.figures.writer import PDFWriter
from croissance.formats.input import TSVReader
from croissance.formats.output import TSVWriter


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Estimate growth rates in growth curves",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("infiles", type=Path, nargs="+")
    parser.add_argument("--input-format", type=str.lower, choices=("tsv",))
    parser.add_argument(
        "--input-time-unit",
        default="hours",
        choices=("hours", "minutes"),
        help="Time unit in time column",
    )
    parser.add_argument(
        "--N0",
        type=float,
        default=0.0,
        help="Baseline for constrained regressions and identifying curve segments in "
        "log space",
    )
    parser.add_argument(
        "--constrain-N0",
        action="store_true",
        help="All growth phases will begin at N0 when this flag is set",
    )
    parser.add_argument(
        "--segment-log-N0",
        action="store_true",
        help="Identify curve segments using log(N-N0) rather than N; increases "
        "sensitivity to changes in exponential growth but has to assume a certain N0",
    )
    parser.add_argument("--output-format", type=str.lower, choices=("tsv",))
    parser.add_argument("--output-suffix", type=str, default=".output")
    parser.add_argument(
        "--output-exclude-default-phase",
        action="store_true",
        help="Do not output phase '0' for each curve",
    )
    parser.add_argument(
        "--figures",
        action="store_true",
        help="Renders a PDF file with figures for each curve",
    )

    group = parser.add_argument_group("Logging")
    group.add_argument(
        "--log-level",
        type=str.upper,
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="Set verbosity of log messages",
    )

    return parser.parse_args(argv)


def setup_logging(level):
    coloredlogs.install(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        level=level,
    )

    return logging.getLogger("croissance")


def main(argv):
    args = parse_args(argv)
    log = setup_logging(level=args.log_level)

    estimator = Estimator(
        constrain_n0=args.constrain_N0,
        segment_log_n0=args.segment_log_N0,
        n0=args.N0,
    )

    log.info("Estimating growth curves ..")
    for filepath in args.infiles:
        log.info("Reading curves from '%s", filepath)
        with TSVReader(filepath) as reader:
            curves = reader.read()

        annotated_curves = {}
        for name, curve in curves:
            if curve.empty:
                log.warning("Skipping empty curve %r", name)
                continue

            log.info("Estimating growth for curve %r", name)
            annotated_curves[name] = estimator.growth(
                normalize_time_unit(curve, args.input_time_unit)
            )

        output_filepath = filepath.with_suffix(args.output_suffix + ".tsv")
        with TSVWriter(output_filepath, args.output_exclude_default_phase) as outwriter:
            for name, annotated_curve in annotated_curves.items():
                outwriter.write(name, annotated_curve)

        if args.figures:
            figure_filepath = filepath.with_suffix(args.output_suffix + ".pdf")

            with PDFWriter(figure_filepath) as figwriter:
                for name, annotated_curve in annotated_curves.items():
                    figwriter.write(name, annotated_curve)

    log.info("Done ..")


def entry_point():
    sys.exit(main(sys.argv[1:]))


if __name__ == "__main__":
    entry_point()
