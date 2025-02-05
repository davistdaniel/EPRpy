Operations on data
============================

After loading the data into an :doc:`EprData <EprData>` object, following functions can be used to perform various operations on the data. Since the data is stored as NumPy arrays, all artihmetic operations 
which are valid on NumPy arrays are also valid on  attributes of :doc:`EprData <EprData>` which are NumPy arrays, such as ``data``, ``x`` and ``y``.

.. note::
    All operations returns a new ``EprData`` object. After each operation, a history entry is added to the history of the ``EprData`` object. 

Scaling
************
Data in an ``EprData`` object can be scaled between two values using the ``scale_between`` method. 
There are two optional inputs ``min_val`` and ``max_val``, which correspond to the minimum and maximum value of the range within which the data will be scaled. 
If no inputs are given, the data is scaled between 0 and 1.

See `how to scale data between two values <notebooks/examples.html#Scaling-data>`_.

Computing Integrals
***********************
Integrals can be calculated using the ``integral`` method of the ``EprData`` class. 
Since CW-EPR data is usually acuqired as firtst-derivatives, the function should be called twice for a double integral calculation. 

See `computing integrals <notebooks/examples.html#Computing-integrals>`_.

Baseline Correction
***********************
Baseline correction in EPRpy supports 1D and 2D data and allows for interactive selection of baseline points. Baseline points in case of 2D data are selected using the first slice of the data.
The baseline can be fitted using linear, polynomial, or spline methods. To correct the baseline, ``baseline_correct`` method of the ``EprData`` class can be used.
Basline correction accepts various inputs :

* *interactive* : If set to True, this will plot the data with an option to sleect points interactively. These points will then be used for the calculatinh the baseline.
* *npts* : Another way of specifying points. When *interactive* is set to False, npts is equal to the number of points at the start and end of the data which is used for baseline correction.
* *method* :  Should be one of 'linear', 'polynomial' and 'spline'.
* *order* : Specifies the polynomial order in case of *method* 'polynomial'.
* *spline_smooth* : Smoothing factor of the spline, in case of *method* 'spline'.

See a `baseline correction example <notebooks/examples.html#Baseline-correction>`_.

Selecting a region
********************
This operation returns a new ``EprData`` object, which corresponds to selected region of the data (or spectrum). The operation is always carried out on the last axis of the data 
and needs a list of indices as input which corresponds to the desired region. See `selecting a region <notebooks/examples.html#Selecting-a-region>`_.

History of data operations
********************************
Any previous ``EprData`` object can be accessed by using the ``history`` attribute of the ``EprData`` object. Each ``EprData`` object stores history of all data operations and the corresponding ``EprData`` object in a list of lists. 
The first item in each list is the description of the data operation and the second item is the corresponding ``EprData`` object. See `how to access history <notebooks/examples.html#History-of-data-operations>`_.