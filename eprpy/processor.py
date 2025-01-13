import numpy as np
from datetime import datetime
from copy import deepcopy
from scipy.interpolate import UnivariateSpline
from tqdm import tqdm


from eprpy.plotter import interactive_points_selector

def _scale_between(eprdata,min_val=None,max_val=None):

    """
    Scale the data in an `EprData` object to a specified range.

    This function normalizes the data of the given `EprData` object to the range 
    defined by `min_val` and `max_val`. If these values are not provided, the 
    default range is [0, 1].

    Parameters
    ----------
    eprdata : EprData
        An instance of the `EprData` class containing the data to be scaled.
    min_val : float, optional
        The minimum value of the desired range. Defaults to 0.
    max_val : float, optional
        The maximum value of the desired range. Defaults to 1.

    Notes
    -----
    - The function modifies the `data` attribute of the input `EprData` object in place.
    - The scaling operation is performed along the last axis of the `data`.
    - A history entry is added to the `EprData` object, documenting the scaling 
      operation and the range used.
    """

    min_val = 0 if min_val is None else min_val
    max_val = 1 if max_val is None else max_val

    data_min = np.min(eprdata.data,axis=-1)
    data_max = np.max(eprdata.data,axis=-1)

    eprdata.data = (eprdata.data-data_min)/(data_max-data_min)
    eprdata.data *= int(max_val-min_val)
    eprdata.data += min_val

    eprdata.history.append([f'{str(datetime.now())} : Data scaled between {min_val} and {max_val}.',deepcopy(eprdata)])


def _integrate(eprdata):
    
    """
    Compute the integral of the data in an `EprData` object.

    This function calculates the cumulative integral of the data in the 
    `EprData` object along the last axis. The integration step size is determined by the spacing of `eprdata.x`.

    Parameters
    ----------
    eprdata : EprData
        An instance of the `EprData` class containing the data to be integrated.

    Notes
    -----
    - The function modifies the `data` attribute of the input `EprData` object in place.
    - The integration is performed along the last axis of the `data`.
    - A history entry is added to the `EprData` object, documenting the integration 
      operation.
    """

    delta_B = np.mean(np.diff(eprdata.x))
    integral = np.cumsum(eprdata.data,axis=-1)*delta_B 

    eprdata.data = integral
    eprdata.history.append([f'{str(datetime.now())} : Integral calculated',deepcopy(eprdata)])

def _baseline_correct(eprdata,interactive=False,
                      npts=10,method='linear',spline_smooth=1e-5,
                      order=2):

    """
    Perform baseline correction on the data in an `EprData` object.

    This function removes the baseline from the data in the `EprData` object. 
    It supports both 1D and 2D data, with optional interactive selection of 
    baseline points for 1D data. The baseline can be fitted using linear, 
    polynomial, or spline methods.

    Parameters
    ----------
    eprdata : EprData
        An instance of the `EprData` class containing the data to be baseline-corrected.
    interactive : bool, optional
        If `True`, enables interactive selection of baseline points for 1D data.
        Defaults to `False`.
    npts : int, optional
        Number of points to use from the start and end of the data for baseline fitting
        when `interactive` is `False`. Defaults to 10.
    method : {'linear', 'polynomial', 'spline'}, optional
        The method used for baseline fitting. Choices are:
        - 'linear': Fits a linear baseline.
        - 'polynomial': Fits a polynomial baseline.
        - 'spline': Fits a spline baseline. 
        Defaults to 'linear'.
    spline_smooth : float, optional
        Smoothing factor for spline fitting. Ignored if `method` is not 'spline'. 
        Defaults to 1e-5.
    order : int, optional
        The order of the polynomial for baseline fitting when `method` is 'polynomial'. 
        Defaults to 2.

    Notes
    -----
    - For 2D data, baseline correction is performed using a separate helper function.
    - For 1D data, baseline points can be selected interactively or automatically 
      based on the specified number of points (`npts`).
    - The function modifies the `data` attribute of the input `EprData` object in place.
    - The computed baseline is stored in the `baseline` attribute of the `EprData` object.
    - A history entry is added to the `EprData` object, documenting the baseline correction.
    """


    x = eprdata.x
    y = eprdata.data

    if y.ndim ==2:
        bc_data,baselines = _baseline_correct_2d(x,y,interactive,
                          npts,method,spline_smooth,order)
        eprdata.data = bc_data
        eprdata.baseline = baselines
        eprdata.history.append([f'{str(datetime.now())} : Baseline corrected',deepcopy(eprdata)])

    elif y.ndim==1:

        if interactive:
            baseline_points = interactive_points_selector(x,y)
        else:
            baseline_points=np.concatenate([np.arange(npts), np.arange(len(y) - npts, len(y))])

        # Use the specified baseline points for fitting
        if baseline_points is not None and len(baseline_points) > 0:
            x_fit = x[baseline_points]
            y_fit = y[baseline_points]
        else:
            # If no baseline points are selected, raise an error or use a default (e.g., endpoints)
            raise ValueError("No baseline points selected. Please select points for baseline correction.")

        # Baseline fitting based on selected method
        if method == "linear":
            coeffs = np.polyfit(x_fit, y_fit, 1)
            baseline = np.polyval(coeffs, x)
        elif method == "polynomial":
            coeffs = np.polyfit(x_fit, y_fit, order)
            baseline = np.polyval(coeffs, x)
        elif method == "spline":
            spline = UnivariateSpline(x_fit, y_fit, s=spline_smooth)
            baseline = spline(x)
        else:
            raise ValueError("Method must be 'linear', 'polynomial', or 'spline'.")

        bc_corr = y - baseline

        eprdata.baseline = baseline
        eprdata.data = bc_corr
        eprdata.history.append([f'{str(datetime.now())} : Baseline corrected',deepcopy(eprdata)])


def _baseline_correct_2d(x,y,interactive=False,
                      npts=10,method='linear',spline_smooth=1e-5,
                      order=2):

    """
    Perform baseline correction on 2D data.

    This function removes the baseline from 2D data, where each row of the input 
    represents a separate spectrum or data series. The baseline can be fitted 
    using linear, polynomial, or spline methods. Optionally, baseline points 
    can be selected interactively.

    Parameters
    ----------
    x : array-like
        The x-axis values corresponding to the data.
    y : array-like
        The 2D data array where each row corresponds to a separate data series.
    interactive : bool, optional
        If `True`, enables interactive selection of baseline points for the 
        first row of the data. Defaults to `False`.
    npts : int, optional
        Number of points to use from the start and end of each row for baseline 
        fitting when `interactive` is `False`. Defaults to 10.
    method : {'linear', 'polynomial', 'spline'}, optional
        The method used for baseline fitting. Choices are:
        - 'linear': Fits a linear baseline.
        - 'polynomial': Fits a polynomial baseline.
        - 'spline': Fits a spline baseline. 
        Defaults to 'linear'.
    spline_smooth : float, optional
        Smoothing factor for spline fitting. Ignored if `method` is not 'spline'. 
        Defaults to 1e-5.
    order : int, optional
        The order of the polynomial for baseline fitting when `method` is 'polynomial'. 
        Defaults to 2.
    
    Returns
    -------
    corrected_data : ndarray
        The 2D data array with baselines removed.
    baselines : ndarray
        The 2D array of computed baselines for each row.

    Notes
    -----
    - Baseline points can be selected interactively for the first row, and the same 
      points are used for all rows.
    - The function supports linear, polynomial, and spline-based baseline fitting.
    - The returned `corrected_data` has the baseline removed, while `baselines` 
      contains the computed baseline for each row of data.
    """

    if interactive:
        baseline_points = interactive_points_selector(x,y[0])
    else:
        baseline_points=np.concatenate([np.arange(npts), np.arange(len(y[0]) - npts, len(y[0]))])
    
    baselines = np.empty_like(y)
    if baseline_points is not None and len(baseline_points) > 0:
        x_fit = x[baseline_points]
        
    for idx,arr in tqdm(enumerate(y)):
        y_fit = arr[baseline_points]
        if method == "linear":
            coeffs = np.polyfit(x_fit, y_fit, 1)
            baseline = np.polyval(coeffs, x)
        elif method == "polynomial":
            coeffs = np.polyfit(x_fit, y_fit, order)
            baseline = np.polyval(coeffs, x)
        elif method == "spline":
            spline = UnivariateSpline(x_fit, y_fit, s=spline_smooth)
            baseline = spline(x)
        else:
            raise ValueError("Method must be 'linear', 'polynomial', or 'spline'.")

        baselines[idx] = baseline
    
    return y-baselines,baselines
