# EPRpy

<img src="https://davistdaniel.github.io/EPRpy/_images/eprpy_logo.png" alt="eprpy_logo" width="300">

[![Static Badge](https://img.shields.io/badge/Version-0.9.0a3-blue?label=Version)](https://github.com/davistdaniel/EPRpy) [![Website](https://img.shields.io/website?url=https%3A%2F%2Fdavistdaniel.github.io%2FEPRpy%2F&up_message=online&down_message=offline&label=Docs)](https://davistdaniel.github.io/EPRpy/) [![GitHub last commit](https://img.shields.io/github/last-commit/davistdaniel/EPRpy)](https://github.com/davistdaniel/EPRpy/commits/main/) 

## About

EPRpy is a Python library designed to streamline the handling, inspection, and processing of Electron Paramagnetic Resonance (EPR) spectroscopic data. The library originated as a collection of scripts I wrote for routine analysis of EPR data acquired on Bruker EPR spectrometers during my academic work. EPRpy focusses on ease of use, enabling quick data visualization, data comparisons, and having transperent as well as highly customisable control over data analysis.

## Installation

To install  and use EPRpy, Python must be installed on your operating system. Python can be downloaded from the [official website](https://www.python.org/downloads/). EPRpy is compatible with Python 3.9 to 3.12 and can be installed with Python's package manager `pip`.

### Installing EPRpy from a pre-built distribution

Run in a terminal (or command prompt) :

`python -m pip install eprpy`

### Installing EPRpy from source

Clone the [EPRpy repository](https://davistdaniel.github.io/EPRpy/) and then navigate to the folder where setup.py file is present.
Then, run in a terminal (or command prompt) :

`python -m pip install .`

## Documentation

For EPRpy documentation, see [here](https://davistdaniel.github.io/EPRpy/). Source files for building the docs using sphinx can be found in docs/source/ .

## Features

* Read and export EPR data acquired on Bruker EPR spectrometers.
* Basic processing capabilities such as interactive baseline correction, integration etc.
* Generate quick plots of 1D and 2D datasets, compare different datasets.

## Upcoming 
* Automated workflow templates for specific EPR experiments
* Documentation for visualization features.

## Limitations
* Supports reading of files only in Bruker BES3T format v.1.2 and upto 2D datasets.

## License
[MIT License](https://github.com/davistdaniel/EPRpy/blob/main/LICENSE)
