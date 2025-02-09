Setting up EPRpy
=====================

* To install **EPRpy**, python needs to be installed. **EPRpy** works with python versions greater than 3.9. Python can be downloaded from the `official website <https://www.python.org/>`_. 
* Python installation and version can be confirmed by typing ``python`` in a terminal or command prompt. Note that the alias for ``python`` can be ``python3`` on your operating system.
* If python and its package manager *pip* is installed, **EPRpy** can be installed using *pip*.

Install from a pre-built distribution
----------------------------------------------

Use python's package manager *pip*. Execute the following in a terminal.

.. code-block:: bash
   
    python -m pip install eprpy

Install from source
----------------------------------------------

Clone the `EPRpy repository <https://davistdaniel.github.io/EPRpy/>`_ and then navigate to the folder where setup.py file is present.
Then, run in a terminal (or command prompt) :

.. code-block:: text
   
    python -m pip install .

Installing **EPRpy** will also install the following python libraries required by **EPRpy**:

* `Matplotlib <https://matplotlib.org/stable/>`_ 
* `NumPy <https://numpy.org/>`_ 
* `SciPy <https://scipy.org/>`_ 
* `tqdm <https://tqdm.github.io/>`_


Importing
---------------

If the installation is successful, you can import **EPRpy** and printing the version as shown below.

.. code-block:: python

    import eprpy as epr
    print(epr.__version__)

Upgrading
---------------

.. code-block:: text
   
    python -m pip install eprpy --upgrade