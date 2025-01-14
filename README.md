# EPRpy 0.9.0

<img src="docs/source/images/eprpy_logo.png" alt="eprpy_logo" width="300">

[![Static Badge](https://img.shields.io/badge/Version-0.9.0-blue?label=Version)](https://github.com/davistdaniel/EPRpy) [![Website](https://img.shields.io/website?url=https%3A%2F%2Fdavistdaniel.github.io%2FEPRpy%2F&up_message=online&down_message=offline&label=Docs)](https://davistdaniel.github.io/EPRpy/) [![GitHub last commit](https://img.shields.io/github/last-commit/davistdaniel/EPRpy)](https://github.com/davistdaniel/EPRpy/commits/main/) 

## About

EPRPy is a python library to streamline handling, inspection and processing of Electron Paramagnetic resonance spectroscopic data.
The library is born out of a collection of scripts I wrote for routine analysis of EPR data and simple presentation of results  during my doctoral work. EPRPy might be of use to you if you need to read, plot and export EPR data acquired on Bruker EPR spectrometers for routine analysis. EPRPy focusses on ease of use, generating quick plots for data inspection and features automated processing workflows for specific EPR experiments.

## Installation

Clone or download this repository and then navigate to the folder where setup.py file is present.
Then, type in a terminal :

`python -m pip install .`

## Documentation

For EPRpy documentation, see [here](https://davistdaniel.github.io/EPRpy/). Source files for building the docs using sphinx can be found in docs/source/ .

## Features

* Read and export EPR data.
* Basic processing capabilities such as interactive baseline correction, integration etc.
* Generate quick plots of 1D and 2D datasets, compare different datasets.

## Upcoming 
* Automated workflows for specific EPR experiments

## Limitations
* Supports reading of files only in Bruker BES3T format v.1.2 and upto 2D datasets.

