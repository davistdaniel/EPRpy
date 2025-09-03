Workflows
===============

The ``workflow`` module in **EPRpy** provides high-level processing pipelines for 
common pulsed-EPR experiments. It is designed to take an ``EprData`` object as input 
and return a fully processed ``EprData`` object, with all intermediate results and 
processing steps preserved for reproducibility in the ``data_dict`` method.

Currently, the module supports workflows for:

* **HYSCORE** (Hyperfine Sublevel Correlation) experiments
* **ESEEM** (Electron Spin Echo Envelope Modulation) experiments

These workflows include baseline correction, windowing, zero-filling, Fourier 
transformation, and frequency axis generation. Optionally, symmetrisation of HYSCORE 
spectra and background fitting strategies for ESEEM are provided.

A workflow can be simply used by loading experimental data with a compatible pulse program :

.. code-block:: python

  # import EPRpy
  import eprpy as epr
  
  # Load data by providing path to .DSC or .DTA file
  hyscore_data = epr.load('hyscore_exp.DSC')

  # process using a workflow, zero fill 1024 points
  hyscore_processed = hyscore_data.workflow(zf=1024)


Have a look at `workflow examples <notebooks/examples.html#Workflows>`_.

Internally, the :ref:`eprworkflowclass` is used when ``EprData.workflow()`` is called. In the example above, ``hyscore_processed`` is an ``EprData`` object, so all methods of ``EprData`` object are also accessible.
Other parameters which are supported for a workflow is explained in the section :ref:`eprworkflowclass`. In the following, the workflow processing steps are elaborated.

HYSCORE processing
--------------------

The workflow supports pulse programs:
    - ``HYSCORE``


HYSCORE datasets are procssed by by:
    - Applying 2D polynomial baseline correction.
    - Windowing with Hamming functions in both dimensions.
    - Zero-filling (optional).
    - Performing a 2D FFT and shifting the result.
    - Symmetrising the FFT data (optional).
    - Returning all results (raw, intermediate, final) in a dictionary.

The output contains frequency axes in MHz and processed spectra suitable for 
plotting and further analysis.

If you have a processed ``EprData`` object from a ``HYSCORE`` data set, the processed arrays can be accessed using ``EprData.data_dict``:

.. code-block:: python

    - 'proc_param': Processing parameters used.
    - 'raw_data': Original raw data.
    - 'baseline_dim1', 'baseline_dim2': Baseline correction results for both dimensions.
    - 'bc_data': Baseline-corrected data.
    - 'window_dim1', 'window_dim2': Window functions applied.
    - 'bc_w_data': Baseline-corrected and windowed data.
    - 'time_axis1', 'time_axis2': Time axes (extended if zero-filled).
    - 'bc_w_zf_data': Zero-filled, baseline-corrected, windowed data.
    - 'frequency_axis1', 'frequency_axis2': Frequency axes for FFT.
    - 'FFT_data': 2D FFT of processed data.
    - 'FFT_shifted_data': FFT data after shift.
    - 'data': Absolute value of shifted FFT (final processed data, optionally symmeterised).
    - 'dims': Frequency axes for plotting.
    - 'is_complex': Boolean indicating if data is complex (always False).
    - 'history': List of processing steps.


ESEEM processing
--------------------

The workflow supports pulse programs:
    - ``2P ESEEM``
    - ``3P ESEEM``
    - ``2P ESEEM vs. B0``
    - ``3P ESEEM vs. B0``
    - ``3P ESEEM vs tau``

ESEEM datasets are processed by:
    - Applying background correction (exponential or polynomial).
    - Windowing with a Hamming function.
    - Zero-filling (optional).
    - Performing a 1D FFT (or along the last axis for 2D data).
    - Returning absolute, shifted FFT spectra along with all intermediate steps.

Results include the processed frequency-domain spectra in MHz, with 
dimensionality preserved for field-dependent ESEEM maps.

If you have a processed ``EprData`` object from a ``ESEEM`` data set, the processed arrays can be accessed using ``EprData.data_dict``:

.. code-block:: python

    - 'proc_param': Processing parameters used.
    - 'raw_data': Original raw data.
    - 'baseline_dim1': Baseline correction results.
    - 'bc_data': Baseline-corrected data.
    - 'window_dim1': Window function applied.
    - 'bc_w_data': Baseline-corrected and windowed data.
    - 'time_axis1': Time axis (extended if zero-filled).
    - 'bc_w_zf_data': Zero-filled, baseline-corrected, windowed data.
    - 'frequency_axis1': Frequency axis for FFT.
    - 'FFT_data': FFT of processed data.
    - 'FFT_shifted_data': FFT data after shift.
    - 'data': Absolute value of shifted FFT (final processed data).
    - 'dims': Frequency axis (and second axis if 2D data).
    - 'is_complex': Boolean indicating if data is complex (always False).
    - 'history': List of processing steps.


.. _eprworkflowclass:

EprWorkflow Class
--------------------

The ``EprWorkflow`` class encapsulates complete workflows for HYSCORE and ESEEM 
data processing. It manages parameters like zero-filling, polynomial order for 
baseline correction, and optional symmetrisation. All results, including raw 
data, corrected data, intermediate steps, and frequency-domain spectra, are 
stored in a dictionary that is updated step by step.

**Parameters**
    - **eprdata** (*EprData*) – Instance of the EprData class.
    - **zf** (*int, optional*) – Number of points to add via zero filling.
    - **poly_order** (*int, optional, default=3*) – Order of the polynomial for baseline correction in case of 3P ESEEM experiments
    - **x_max** (*float, optional*) – Upper bound of the Hamming window.
    - **pick_eseem_points** (*bool, default=False*) – Whether to pick points along the ESEEM decay curve for background calculation. If False, all data points are used.
    - **symmeterise** (*bool or str, default=False*) – If set, symmetrises HYSCORE FFT results across diagonal or anti-diagonal.

Both ``hyscore()`` and ``eseem()`` return a **dictionary** containing raw data, 
intermediate results, processing parameters, and final spectra.  
Some keys are primarily useful for debugging, while others are essential for 
end-users who wish to analyse or visualise results.


