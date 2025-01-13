Loading EPR data
============================

For loading data acuqired on Bruker spectrometers, **EPRpy** needs the path to either the ``.DSC`` or ``.DTA`` file. The ``.DSC`` and ``.DTA`` 
must be in the same folder. In case of some 2D-data, an accompanying ``.GF`` is also required in the same folder.

Data can be loaded into an ``EprData`` object by using the ``load(filepath)`` function as follows.

.. code-block:: python

  # import EPRpy
  import eprpy as epr
  
  # Load data by providing path to .DSC or .DTA file
  epr_data = epr.load('tempo.DSC')


``epr_data`` is an :doc:`EprData <EprData>` data object with various accessible attributes. For instance. the loaded data can be accessed by ``epr_data.data``.