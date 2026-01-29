# Croissance

| Information           | Links                                                                                                                                                                                                                                                                                                                                                       |
| :-------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Package**           | [![PyPI Latest Release](https://img.shields.io/pypi/v/croissance.svg)][croissance-pypi] [![Supported versions](https://img.shields.io/pypi/pyversions/croissance.svg)][croissance-pypi] [![Supported implementations](https://img.shields.io/pypi/implementation/croissance.svg)][croissance-pypi] [![License: Apache2](https://img.shields.io/badge/License-Apache2-blue.svg)][apache2-license] |
| **Documentation**     | [![View - Documentation](https://img.shields.io/badge/view-Documentation-blue?style=flat)][croissance-docs] [![made-with-sphinx-doc](https://img.shields.io/badge/Made%20with-Sphinx-1f425f.svg)](https://www.sphinx-doc.org/) ![Docs](https://readthedocs.org/projects/croissance/badge/?style=flat) [![CC BY 4.0][cc-by-shield]][croissance-license]            |
| **Build**             | [![CI](https://github.com/biosustain/croissance/actions/workflows/cicd.yml/badge.svg)][ci-gh-action]                                                                                                                                                                                                                                             |
| **Discuss on GitHub** | [![GitHub issues](https://img.shields.io/github/issues/biosustain/croissance)][issues] [![GitHub pull requests](https://img.shields.io/github/issues-pr/biosustain/croissance)][pulls]                                                                                                                                                |


## Description

A tool for estimating growth rates in growth curves. The tool fits $\lambda \cdot e^{\mu x} + N_0$ to any candidate growth phases of the growth curve that have increasing growth, i.e. where both the first and second derivative of the growth function are positive. To identify these phases reliably, the tool utilizes a custom smoothing function that addresses problems other smoothing methods have with growth curves that have regions with varying levels of noise (e.g. lots of noise in the beginning, then less noise after growth starts, then more noise in the stationary phase).

The parameter $N_0$ represents the background/blank OD reading (not seeding OD) and can optionally be constrained. This is recommended if the value is known.

The growth rate in calculated growth phases can only be properly compared if their seeding OD (when the organism is at its initial population) points to a similar stage of actual growth.

Intercept (λ) reported by this package can be used as indicator of lag if SNR is sufficiently high.

## Installation

To install `croissance`, use Python 3.x `pip`:

```bash
pip3 install croissance
```

## Usage

Croissance can be used from command-line or as a Python library. The input to the command-line tool is generally one or more `*.tsv` files (tab-separated values) with the following format:

| time | A1   | A2   | ... |
| ---- | ---- | ---- | --- |
| 0.0  | 0.0  | 0.01 | ... |
| 0.17 | 0.14 | 0.06 | ... |
| ...  | ...  | ...  | ... |

Each sample should be recorded in its own column with the sample name in the header row. The time unit is hours and the value unit should be OD or some value correlating with OD.

To process this file, enter:

```bash
croissance example.tsv
```

The output will be generated at `example.output.tsv`. The output is formatted with column headers: `name` (sample name), `phase` (nth growth phase), `start` (start time), `end` (end time), `slope` (μ), `intercept` (λ), `n0` ($N_0$) and a few others. By default, each sample is represented by at least one row, containing phase "0". This is simply the highest ranking phase if one was found for this curve; otherwise the remaining columns are empty.

---

To also output a PDF files with figures (`example.output.pdf`), enter:

```bash
croissance --figures example.tsv
```

[![Example figure](https://cloud.githubusercontent.com/assets/74085/21225960/abfa9a4a-c2d3-11e6-85c6-88b1db24723c.png)](#)

---

To see a description of all the command-line options available, enter `croissance --help`.

For use from Python, provide your growth curve as a `pandas.Series` object. The growth rates are estimated using `croissance.process_curve(curve)`. The return value is a `namedtuple` object with attributes `series`, `outliers` and `growth_phases`. Each growth phase has the attributes `start` (start time), `end` (end time), `slope` (μ), `intercept` (λ), `n0` ($N_0$), as well as other attributes such as `SNR` (signal-to-noise ratio of the fit) and `rank`.

```python
from croissance import process_curve

result = process_curve(my_curve)
print(result.growth_phases)
```

[croissance-pypi]: https://pypi.org/project/croissance/
[croissance-license]: https://github.com/biosustain/croissance/blob/main/LICENSE.md
[croissance-docs]: https://croissance.readthedocs.io/
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg
[apache2-license]: https://www.apache.org/licenses/LICENSE-2.0
[ci-gh-action]: https://github.com/biosustain/croissance/actions/workflows/cicd.yml
[issues]: https://github.com/biosustain/croissance/issues
[pulls]: https://github.com/biosustain/croissance/pulls
[biosustain_gh]: https://biosustain.github.io/
[Biosustain]: https://www.biosustain.dtu.dk/
[new-issue]: https://github.com/biosustain/croissance/issues/new

