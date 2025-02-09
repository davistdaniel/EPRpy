.. EPRpy documentation master file, created by
   sphinx-quickstart on Fri Dec 20 10:05:50 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to **EPRpy**'s documentation
======================================

.. image:: images/eprpy_logo.png
   :width: 400px
   :align: center

**EPRpy** is a Python library designed to streamline the handling, inspection, and processing of Electron Paramagnetic Resonance (EPR) spectroscopic data acquired on Bruker EPR spectrometers. 
**EPRpy** focusses on ease of use, enabling quick data visualization, data comparisons, and having transperent as well as highly customisable control over data analysis.


Quick start
----------------------
If you have python installed, install EPRpy by executing in a terminal :

.. code-block:: bash
   
    python -m pip install eprpy

An example workflow with **EPRpy** is shown below.

.. code-block:: python

  # import EPRpy
  import eprpy as epr
  
  # Load data by providing path to .DSC or .DTA file
  epr_data = epr.load('tempo.DSC')
    
  # plot
  fig,ax = epr_data.plot(interactive=True)
  
.. image:: images/interactive_plot.gif


Using EPRpy
----------------------

.. toctree::
   :maxdepth: 1
   :caption: User guide

   installation
   loading
   processing
   plotting
   EprData
   Examples

