import numpy as np
from datetime import datetime
from copy import deepcopy
from scipy.interpolate import UnivariateSpline
from scipy.ndimage import gaussian_filter1d

# EPRpy
from eprpy.plotter import interactive_points_selector

def _scale_between(eprdata, min_val=None, max_val=None):
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
    eprdata_proc = deepcopy(eprdata)

    min_val = 0 if min_val is None else min_val
    max_val = 1 if max_val is None else max_val

    data_min = np.min(eprdata_proc.data, axis=-1, keepdims=True)
    data_max = np.max(eprdata_proc.data, axis=-1, keepdims=True)

    eprdata_proc.data = (eprdata_proc.data - data_min) / (data_max - data_min)
    eprdata_proc.data *= int(max_val - min_val)
    eprdata_proc.data += min_val

    eprdata_proc.history.append(
        [
            f"{str(datetime.now())} : Data scaled between {min_val} and {max_val}.",
            deepcopy(eprdata_proc),
        ]
    )

    return eprdata_proc


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
    eprdata_proc = deepcopy(eprdata)

    delta_B = np.mean(np.diff(eprdata_proc.x))
    integral = np.cumsum(eprdata_proc.data, axis=-1) * delta_B

    eprdata_proc.data = integral
    eprdata_proc.history.append(
        [f"{str(datetime.now())} : Integral calculated", deepcopy(eprdata_proc)]
    )

    return eprdata_proc


def _baseline_correct(
    eprdata, interactive=False, npts=10, method="linear", spline_smooth=1e-5, order=2
):
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

    eprdata_proc = deepcopy(eprdata)

    x = eprdata_proc.x
    y = eprdata_proc.data

    if y.ndim == 2:
        bc_data, baselines = _baseline_correct_2d(
            x, y, interactive, npts, method, spline_smooth, order
        )
        eprdata_proc.data = bc_data
        eprdata_proc.baseline = baselines
        eprdata_proc.history.append(
            [f"{str(datetime.now())} : Baseline corrected", deepcopy(eprdata_proc)]
        )

    elif y.ndim == 1:
        if interactive:
            baseline_points = interactive_points_selector(x, y)
        else:
            baseline_points = np.concatenate(
                [np.arange(npts), np.arange(len(y) - npts, len(y))]
            )

        # Use the specified baseline points for fitting
        if baseline_points is not None and len(baseline_points) > 0:
            x_fit = x[baseline_points]
            y_fit = y[baseline_points]
        else:
            # If no baseline points are selected, raise an error or use a default (e.g., endpoints)
            raise ValueError(
                "No baseline points selected. Please select points for baseline correction."
            )

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

        eprdata_proc.baseline = baseline
        eprdata_proc.data = bc_corr
        eprdata_proc.history.append(
            [f"{str(datetime.now())} : Baseline corrected", deepcopy(eprdata_proc)]
        )

    return eprdata_proc


def _baseline_correct_2d(
    x, y, interactive=False, npts=10, method="linear", spline_smooth=1e-5, order=2
):
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
        baseline_points = interactive_points_selector(x, y[0])
    else:
        baseline_points = np.concatenate(
            [np.arange(npts), np.arange(len(y[0]) - npts, len(y[0]))]
        )

    baselines = np.empty_like(y)
    if baseline_points is not None and len(baseline_points) > 0:
        x_fit = x[baseline_points]

    for idx, arr in enumerate(y):
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

    return y - baselines, baselines


def _derivative(eprdata, sigma=1, axis=-1):
    """
    Compute the derivative of the data in an `EprData` object.

    This function calculates the first derivative of the data in the
    `EprData` object using a Gaussian filter for smoothing. The derivative is computed
    along the specified axis, with the smoothness controlled by the `sigma` parameter.

    Parameters
    ----------
    eprdata : EprData
        An instance of the `EprData` class containing the data to be differentiated.
    sigma : float, optional
        Standard deviation of the Gaussian kernel (controls the smoothness), by default 1.
    axis : int, optional
        Axis along which to compute the derivative, by default -1 (last axis).

    Returns
    -------
    EprData
        A new `EprData` object with the derivative of the data, retaining the original data
        and history for reference.

    Notes
    -----
    - The function does not modify the original `EprData` object in place but returns a new one.
    - The derivative is computed using `scipy.ndimage.gaussian_filter1d`, which smooths the data
    using a Gaussian kernel before calculating the first derivative.
    - If the data is complex, the real and imaginary parts are differentiated separately.
    - A history entry is added to the `EprData` object, documenting the derivative calculation operation.
    """

    eprdata_proc = deepcopy(eprdata)

    if np.iscomplexobj(eprdata_proc.data):
        real_deriv = gaussian_filter1d(
            eprdata_proc.data.real, sigma=sigma, order=1, axis=axis, mode="nearest"
        )
        imag_deriv = gaussian_filter1d(
            eprdata_proc.data.imag, sigma=sigma, order=1, axis=axis, mode="nearest"
        )
        derivative = real_deriv + 1j * imag_deriv
    else:
        derivative = gaussian_filter1d(
            eprdata.data, sigma=sigma, order=1, axis=axis, mode="nearest"
        )

    eprdata_proc.data = derivative
    eprdata_proc.history.append(
        [f"{str(datetime.now())} : Derivative calculated", deepcopy(eprdata_proc)]
    )

    return eprdata_proc

