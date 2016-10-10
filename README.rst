
==========
Croissance
==========

.. image:: https://img.shields.io/travis/biosustain/croissance/master.svg?style=flat-square
    :target: https://travis-ci.org/biosustain/croissance



Description
===========

A tool for estimating growth rates in growth curves. The tool fits λ ⋅ e :sup:`μ⋅x` + N :sub:`0` to any candidate growth phases of the growth curve that have increasing growth, i.e. where both the first and second derivative of the growth function are positive. To identify these phases reliably, the tool utilizes a custom smoothing function that addresses problems other smoothing methods have with growth curves that have regions with varying levels of noise (e.g. lots of noise in the beginning, then less noise after growth starts, then more noise in the stationary phase). 

The parameter N :sub:`0` of the model can optionally be constrained. This is recommended if the value is known. Growth is only comparable between growth phases if their N :sub:`0` (initial population) parameter is at a similar stage of true growth.

Installation
============

To install ``croissance`` with Python 3.x use:

::

    pip3 install croissance


Usage
=====

Croissance can be used from command-line or as a Python library. The input to the command-line tool is generally one or more `*.tsv` files with the following format:

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

To also output a PDF files with figures (``example.output.pdf``), enter:

::

    croissance --figures example.tsv 

To see all the command-line options available, enter ``croissance``.

For use from Python, provide your growth curve as a ``pandas.Series`` object. The growth rates are estimated using ``croissance.process_curve(curve)``. The return value is a ``namedtuple`` object with attributes ``series``, ``outliers`` and ``growth_phases`` . Each growth phase has the attributes ``start`` (start time), ``end`` (end time), ``slope`` (μ), ``intercept`` (λ), ``n0`` (N :sub:`0`), as well as other attributes such as ``SNR`` (signal-to-noise ratio of the fit) and ``rank``.

::

    from croissance import process_curve

    result = process_curve(my_curve)
    print(result.growth_phases)
