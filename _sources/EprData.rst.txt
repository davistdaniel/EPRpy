EprData class
============================


``EprData`` is the main data handling class of ``EPRpy``. The attributes of this class are described below.

* **data_dict** : A python dictionary with the data, acquisition parameters, filepath etc.
* **filepath** : The filepath of the .DSC or .DTA file 
* **data** : The raw data which is read from the .DTA file stored as a NumPy array
* **dims** : A list of arrays which define each dimension of the data. For instance, for a simple 1D-EPR spectrum, dims contains the field values.
* **x** : NumPy array corresponding to the abscissa of the data
* **y** : NumPy array corresponding to the ordinate of the data (only defined in case of 2-D data, otherwise is ``None``.)
* **is_complex** : A boolean flag which indicates if the data is of complex type (i.e. also contains imaginary values)
* **acq_param** : A python dictionary of acquisition parameters which were read from the .DSC file.
* **history** : Describes the history of the ``EprData`` object. This attribute is a list of lists, with each element in the main list containing a string desrcribing the processing step and the corresponding ``EprData`` object.
