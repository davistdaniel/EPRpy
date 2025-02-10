Loading and exporting data
============================

Loading data
------------------

For loading data acquired on Bruker spectrometers, **EPRpy** needs the path to either the ``.DSC`` or ``.DTA`` file. The ``.DSC`` and ``.DTA`` 
must be in the same folder. In case of some 2D-data, an accompanying ``.GF`` is also required in the same folder.

Data can be loaded into an ``EprData`` object by using the ``load(filepath)`` function as follows.

.. code-block:: python

  # import EPRpy
  import eprpy as epr
  
  # Load data by providing path to .DSC or .DTA file
  epr_data = epr.load('tempo.DSC')


``epr_data`` is an :doc:`EprData <EprData>` data object with various :doc:`accessible attributes <EprData>`. For instance. the loaded data can be accessed by ``epr_data.data`` and 
acquisition parameters can be accessed by ``epr_data.acq_param``.


Exporting data
-----------------

Data is stored in the form of Numpy arrays, therfore, you can use numpy functions for exporting data as shown below.

.. code-block:: python

  # import EPRpy
  import eprpy as epr
  
  # Load data by providing path to .DSC or .DTA file
  epr_data = epr.load('tempo.DSC')

  # export 
  ## epr_data.x contains the abscissa (field values in this case)
  ## epr_data.data contains the spectrum (or intensity)

  out_data = np.array([epr_data.x,epr_data.data])
  np.savetxt('tempo.txt',out_data.T)

Read more about `input and output of NumPy arrays <https://numpy.org/doc/stable/reference/routines.io.html>`_.