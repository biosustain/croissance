
==========
Croissance
==========

.. image:: https://img.shields.io/travis/biosustain/croissance/master.svg?style=flat-square
    :target: https://travis-ci.org/biosustain/croissance

.. image:: https://img.shields.io/pypi/v/croissance.svg?style=flat-square
    :target: https://pypi.python.org/pypi/croissance

.. image:: https://img.shields.io/pypi/l/croissance.svg?style=flat-square
    :target: https://pypi.python.org/pypi/croissance
    
.. image:: https://zenodo.org/badge/70239371.svg
   :target: https://zenodo.org/badge/latestdoi/70239371    

Description
===========

A tool for estimating growth rates in growth curves. The tool fits λ ⋅ e :sup:`μ⋅x` + N :sub:`0` to any candidate growth phases of the growth curve that have increasing growth, i.e. where both the first and second derivative of the growth function are positive. To identify these phases reliably, the tool utilizes a custom smoothing function that addresses problems other smoothing methods have with growth curves that have regions with varying levels of noise (e.g. lots of noise in the beginning, then less noise after growth starts, then more noise in the stationary phase). 

The parameter N :sub:`0` represents the background/blank OD reading (not seeding OD) and can optionally be constrained. This is recommended if the value is known.

The growth rate in calculated growth phases can only be properly compared if their seeding OD (when the organism is at its initial population) points to a similar stage of actual growth.

Intercept (λ) reported by this package can be used as indicator of lag if SNR is sufficiently high.

Installation
============

To install ``croissance``, use Python 3.x `pip`:

::

    pip3 install croissance


Usage
=====

Croissance can be used from command-line or as a Python library. The input to the command-line tool is generally one or more `*.tsv` files (tab-separated values) with the following format:

===== ===== ===== =====
time  A1    A2    ...
===== ===== ===== =====
0.0   0.0   0.01  ...
0.17  0.14  0.06  ...
...   ...   ...   ...
===== ===== ===== =====

Each sample should be recorded in its own column with the sample name in the header row. The time unit is hours and the value unit should be OD or some value correlating with OD.

To process this file, enter:

::

    croissance example.tsv 
    
The output will be generated at ``example.output.tsv``. The output is formatted with column headers: ``name`` (sample name), ``phase`` (nth growth phase), ``start`` (start time), ``end`` (end time),  ``slope`` (μ), ``intercept`` (λ), ``n0`` (N :sub:`0`) and a few others. By default, each sample is represented by at least one row, containing phase "0". This is simply the highest ranking phase if one was found for this curve; otherwise the remaining columns are empty. 

----

To also output a PDF files with figures (``example.output.pdf``), enter:

::

    croissance --figures example.tsv 


.. image:: https://cloud.githubusercontent.com/assets/74085/21225960/abfa9a4a-c2d3-11e6-85c6-88b1db24723c.png
    :target: #
    :align: center
    
----

To see a description of all the command-line options available, enter ``croissance --help``.

For use from Python, provide your growth curve as a ``pandas.Series`` object. The growth rates are estimated using ``croissance.process_curve(curve)``. The return value is a ``namedtuple`` object with attributes ``series``, ``outliers`` and ``growth_phases`` . Each growth phase has the attributes ``start`` (start time), ``end`` (end time), ``slope`` (μ), ``intercept`` (λ), ``n0`` (N :sub:`0`), as well as other attributes such as ``SNR`` (signal-to-noise ratio of the fit) and ``rank``.

::

    from croissance import process_curve

    result = process_curve(my_curve)
    print(result.growth_phases)
