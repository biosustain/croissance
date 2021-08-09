# -*- coding: utf-8 -*-
# Copyright 2015 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from setuptools import setup, find_packages

setup(
    name="croissance",
    version="1.2.0",
    packages=find_packages(),
    url="https://github.com/biosustain/croissance",
    author="Lars Schöning",
    author_email="lays@biosustain.dtu.dk",
    description="A tool for estimating growth rates in growth curves.",
    long_description=open("README.rst", encoding="utf-8").read(),
    license="Apache License Version 2.0",
    entry_points={
        "console_scripts": [
            "croissance = croissance.main:entry_point",
        ],
    },
    install_requires=[
        "coloredlogs>=14.0.0",
        "matplotlib>=1.4.3",
        "numpy>=1.9.1",
        "pandas>=0.18.0",
        "scipy>=0.14.0",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: Apache Software License",
    ],
)
