#!/usr/bin/env python
import argparse
import logging
import multiprocessing
import signal
import sys
import traceback

from pathlib import Path

import coloredlogs

from croissance import Estimator
from croissance.estimation.util import normalize_time_unit
from croissance.figures.writer import PDFWriter
from croissance.formats.input import TSVReader
from croissance.formats.output import TSVWriter


class EstimatorWrapper:
    def __init__(self, args):
        self.estimator = Estimator(
            constrain_n0=args.constrain_N0,
            segment_log_n0=args.segment_log_N0,
            n0=args.N0,
        )

        self.input_time_unit = args.input_time_unit

    def __call__(self, values):
        filepath, idx, name, curve = values

        try:
            normalized_curve = normalize_time_unit(curve, self.input_time_unit)
            annotated_curve = self.estimator.growth(normalized_curve, name)

            return (filepath, idx, name, annotated_curve)
        except Exception:
            log = logging.getLogger("croissance")
            log.error("Unhandled exception while annotating %r:", name)
            for line in traceback.format_exc().splitlines():
                log.error("%s", line)


def init_worker():
    # Ensure that KeyboardInterrupt exceptions only occur in the main thread
    signal.signal(signal.SIGINT, signal.SIG_IGN)


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

    parser.add_argument(
        "--threads",
        type=int,
        default=1,
        help="Max number of threads to use during growth estimation",
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

    curves = []
    for filepath in args.infiles:
        log.info("Reading curves from '%s", filepath)
        with TSVReader(filepath) as reader:
            for idx, (name, curve) in enumerate(reader.read()):
                if curve.empty:
                    log.warning("Skipping empty curve %r", name)
                    continue

                curves.append((filepath, idx, name, curve))
    log.info("Collected a total of %i growth curves", len(curves))

    # Dont spawn more processes than tasks
    args.threads = max(1, min(args.threads, len(curves)))
    log.info("Annotating growth curves using %i threads", args.threads)

    return_code = 0
    annotated_curves = {filepath: [] for filepath in args.infiles}
    with multiprocessing.Pool(processes=args.threads, initializer=init_worker) as pool:
        async_calculation = pool.imap_unordered(EstimatorWrapper(args), curves)

        for nth, result in enumerate(async_calculation, start=1):
            if result is None:
                return_code = 1
                continue

            (filepath, idx, name, curve) = result
            log.info("Annotated curve %i of %i: %s", nth, len(curves), name)

            annotated_curves[filepath].append((idx, name, curve))

    for filepath in args.infiles:
        output_filepath = filepath.with_suffix(args.output_suffix + ".tsv")
        log.info("Writing annotated curves to '%s'", output_filepath)

        with TSVWriter(output_filepath, args.output_exclude_default_phase) as outwriter:
            for _, name, annotated_curve in sorted(annotated_curves[filepath]):
                outwriter.write(name, annotated_curve)

        if args.figures:
            figure_filepath = filepath.with_suffix(args.output_suffix + ".pdf")
            log.info("Writing PDFs to '%s'", figure_filepath)

            with PDFWriter(figure_filepath) as figwriter:
                for _, name, annotated_curve in sorted(annotated_curves[filepath]):
                    figwriter.write(name, annotated_curve)

    log.info("Done ..")

    return return_code


def entry_point():
    sys.exit(main(sys.argv[1:]))


if __name__ == "__main__":
    entry_point()
