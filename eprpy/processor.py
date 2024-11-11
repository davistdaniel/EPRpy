import numpy as np
from datetime import datetime
from copy import deepcopy
from scipy.interpolate import UnivariateSpline
from tqdm import tqdm


from eprpy.plotter import interactive_points_selector

def _scale_between(eprdata,min_val=None,max_val=None):

    min_val = 0 if min_val is None else min_val
    max_val = 1 if max_val is None else max_val

    data_min = np.min(eprdata.data,axis=-1)
    data_max = np.max(eprdata.data,axis=-1)

    eprdata.data = (eprdata.data-data_min)/(data_max-data_min)
    eprdata.data *= int(max_val-min_val)
    eprdata.data += min_val

    eprdata.history.append([f'{str(datetime.now())} : Data scaled between {min_val} and {max_val}.',deepcopy(eprdata)])


def _integrate(eprdata):

    delta_B = np.mean(np.diff(eprdata.x))
    integral = np.cumsum(eprdata.data,axis=-1)*delta_B 

    eprdata.data = integral
    eprdata.history.append([f'{str(datetime.now())} : Integral calculated',deepcopy(eprdata)])

def _baseline_correct(eprdata,interactive=False,
                      npts=10,method='linear',spline_smooth=1e-5,
                      order=2):

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

    if interactive:
        baseline_points = interactive_points_selector(x,y[0])
    else:
        baseline_points=np.concatenate([np.arange(npts), np.arange(len(y) - npts, len(y))])
    
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
