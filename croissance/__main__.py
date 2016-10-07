#!/usr/bin/env python
import argparse

import sys

from tqdm import tqdm

from croissance import Estimator
from croissance.figures import PDFWriter
from croissance.formats.input import TSVReader
from croissance.formats.output import TSVWriter

parser = argparse.ArgumentParser(description="Estimate growth rates in growth curves")
parser.add_argument('infiles', type=argparse.FileType('r'), nargs='+')
parser.add_argument('--input-format', type=str, default='tsv')
parser.add_argument('--constrain-N0', action='store_true')
parser.add_argument('--N0', type=float, default=0.0)
parser.add_argument('--output-format', type=str, default='tsv')
parser.add_argument('--output-suffix', type=str, default='.output')
parser.add_argument('--output-exclude-default-phase', type=bool, default=False)
parser.add_argument('--figures', action='store_true')


def main():
    args = parser.parse_args()

    if args.input_format.lower() != 'tsv':
        raise NotImplementedError()

    if args.output_format.lower() != 'tsv':
        raise NotImplementedError()

    reader = TSVReader()

    estimator = Estimator(constrain_n0=args.constrain_N0,
                          n0=args.N0)

    try:
        for infile in tqdm(args.infiles, unit='infile'):
            outfile = open('{}{}.tsv'.format(infile.name[:-4], args.output_suffix), 'w')

            if args.figures:
                figfile = open('{}{}.pdf'.format(infile.name[:-4], args.output_suffix), 'wb')
                figwriter = PDFWriter(figfile)

            outwriter = TSVWriter(outfile, include_default_phase=not args.output_exclude_default_phase)

            for name, curve in tqdm(list(reader.read(infile)), unit='curve'):
                annotated_curve = estimator.growth(curve)

                outwriter.write(name, annotated_curve)

                if args.figures:
                    figwriter.write(name, annotated_curve)

            outwriter.close()

            if args.figures:
                figwriter.close()
    except KeyboardInterrupt:
        pass

    print()


if __name__ == '__main__':
    sys.exit(main())
