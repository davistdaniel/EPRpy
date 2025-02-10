# EPRpy

<img src="https://davistdaniel.github.io/EPRpy/_images/eprpy_logo.png" alt="eprpy_logo" width="300">

![PyPI - Version](https://img.shields.io/pypi/v/eprpy) [![Website](https://img.shields.io/website?url=https%3A%2F%2Fdavistdaniel.github.io%2FEPRpy%2F&up_message=online&down_message=offline&label=Docs)](https://davistdaniel.github.io/EPRpy/) [![GitHub last commit](https://img.shields.io/github/last-commit/davistdaniel/EPRpy)](https://github.com/davistdaniel/EPRpy/commits/main/) ![PyPI - License](https://img.shields.io/pypi/l/eprpy)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/eprpy)

## About

EPRpy is a Python library designed to streamline the handling, inspection, and processing of Electron Paramagnetic Resonance (EPR) spectroscopic data. The library originated as a collection of scripts I wrote for routine analysis of EPR data acquired on Bruker EPR spectrometers during my academic work. EPRpy focusses on ease of use, enabling quick data visualization (see below), data comparisons, and having transparent as well as highly customisable control over data analysis.

<img src="https://github.com/davistdaniel/EPRpy/raw/main/docs/source/images/title_gif.gif" alt="title_gif">

## Installation

If you have python installed, EPRpy can be installed using *pip*. Execute the following in a terminal (or command prompt) :

`python -m pip install eprpy`

Further installation instructions can be found in the [documentation](https://davistdaniel.github.io/EPRpy/).

## Documentation

For EPRpy documentation, see [here](https://davistdaniel.github.io/EPRpy/). Source files for building the documentation using sphinx can be found in docs/source/ .

## Features

* Read and export EPR data acquired on Bruker EPR spectrometers.
* Basic processing capabilities such as [interactive baseline correction](https://davistdaniel.github.io/EPRpy/notebooks/examples.html#Baseline-correction), integration etc.
* [Interactive data inspection](https://davistdaniel.github.io/EPRpy/plotting.html#interactive-plots) for 1D and 2D datasets.
* Generate quick plots of 1D and 2D datasets, compare different datasets.

## Upcoming 
* Automated workflow templates for specific EPR experiments

## Limitations
* Supports reading of files only in Bruker BES3T format v.1.2 and upto 2D datasets.

## License
[MIT License](https://github.com/davistdaniel/EPRpy/blob/main/LICENSE)
