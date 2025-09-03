import numpy as np
import warnings
import time
from copy import deepcopy

# EPRpy
from eprpy.processor import _baseline_correct_2d, _baseline_correct_1d


def _hamming_window(x, x_max=None):
    """
    Hamming window function

    Parameters
    ----------
    x : ndarray
        Input array whose length determines the window size.
    x_max : int, optional
        Maximum length of the window. If None, uses the length of `x`.

    Returns
    -------
    ndarray
        Hamming window array matching the length of `x`.
    """
    if x_max is None:
        x_max = x.size
    window = 0.54 + 0.46 * np.cos(np.linspace(0, np.pi, num=x_max))
    if window.size < x.size:
        return np.pad(
            window,
            pad_width=(0, x.size - window.size),
            mode="constant",
            constant_values=window[-1],
        )
    else:
        return window[: x.size]


def _generate_freq_axis(eprdata, timeaxis):
    """
    Generate a frequency axis based on acquisition parameters and time axis.

    Parameters
    ----------
    eprdata : object
        EprData instance
    timeaxis : numpy.ndarray
        Array representing the time axis.

    Returns
    -------
    numpy.ndarray
        Frequency axis generated based on the time axis and acquisition parameters.

    Warns
    -----
    UserWarning
        If there is an error reading the "XUNI" acquisition parameter.

    Notes
    -----
    The frequency axis is calculated using the time difference and a scaling factor
    determined by the time unit ("XUNI"). Supported units are "ns", "ms", "us", and "s".
    """
    try:
        x_unit = eprdata.acq_param["XUNI"]
    except Exception as e:
        x_unit = None
        x_unit_warn = f"Error while reading x units : {e}"
        warnings.warn(x_unit_warn)

    if x_unit in ["ns", "ms"]:
        x_factor = 1000
    elif x_unit in ["us", "s"]:
        x_factor = 1
    else:
        x_factor = 1

    freq_limit1 = x_factor / (abs(timeaxis[0] - timeaxis[1])) * 0.5

    return np.linspace(-freq_limit1, freq_limit1, timeaxis.size)


class EprWorkflow:
    """

    Parameters
    ----------
    eprdata : ErpData
        An instance of EprData class
    zf : int, optional
        Number of points to use for zero filling
    poly_order : int, optional, default 3
        Order of polynomial used for fitting and baseline correction
    x_max : float, optional, default None
        Upper bound of the window. If None, the maximum of `x` is used.
    pick_eseem_points: bool, default False
        If True, points are picked along the ESEEM decay curve and is used for background calculation.
    """

    def __init__(
        self,
        eprdata,
        zf=0,
        poly_order=3,
        x_max=None,
        pick_eseem_points=False,
        symmetrise=False,
        verbose=False
    ):
        self.eprdata = deepcopy(eprdata)

        if type(zf) is not int:
            raise TypeError(f"zf must be of type int but got {type(zf)}")
        self.zf = (0, zf)

        if type(poly_order) is not int:
            raise TypeError(
                f"poly_order parameter must be of type int but got {type(poly_order)}"
            )
        self.poly_order = poly_order

        self.x_max = x_max
        self.pick_eseem_points = pick_eseem_points
        self.symmetrise = symmetrise,
        self.verbose = verbose


    def hyscore(self):
        """
        Processes a HYSCORE (Hyperfine Sublevel Correlation) EPR dataset with baseline correction, windowing, zero-filling, and 2D FFT.

        This workflow is designed for datasets acquired with the 'HYSCORE' pulse program. It performs the following steps:
        - Checks if the pulse program is 'HYSCORE' and issues a warning if not.
        - Stores processing parameters in the output dictionary.
        - Applies baseline correction along both dimensions using polynomial fitting.
        - Applies Hamming window functions to both dimensions.
        - Optionally zero-fills the data if specified.
        - Computes the time axes for both dimensions.
        - Generates frequency axes for both dimensions.
        - Performs a 2D FFT and shifts the result.
        - Stores the absolute value of the shifted FFT as the processed data.
        - Optionally symmetrise the FFT data if requested via the `symmetrise` attribute.
        - Updates the output dictionary with all intermediate and final results, including processing history.

        Returns
        -------
        dict
            A dictionary containing the processed HYSCORE dataset, including:
            - 'proc_param': Processing parameters used.
            - 'raw_data': Original raw data.
            - 'baseline_dim1', 'baseline_dim2': Baseline correction results for both dimensions.
            - 'bc_data': Baseline-corrected data.
            - 'window_dim1', 'window_dim2': Window functions applied.
            - 'bc_w_data': Baseline-corrected and windowed data.
            - 'time_axis1', 'time_axis2': Time axes (zero-filled if specified).
            - 'bc_w_zf_data': Zero-filled, baseline-corrected, windowed data.
            - 'frequency_axis1', 'frequency_axis2': Frequency axes for FFT.
            - 'FFT_data': 2D FFT of processed data.
            - 'FFT_shifted_data': FFT data after shift.
            - 'data': Absolute value of shifted FFT (final processed data, optionally symmeterised).
            - 'dims': Frequency axes for plotting.
            - 'is_complex': Boolean indicating if data is complex (always False).
            - 'history': List of processing steps.
        """

        vprint = print if self.verbose is True else lambda *args, **kwargs: None
        start_time = time.time()
        

        if self.eprdata.pulse_program != "HYSCORE":
            raise ValueError(f"Unknown pulse program : {self.eprdata.pulse_program}")
        
        vprint("Starting HYSCORE workflow...")
        hyscore_out_dict = self.eprdata.data_dict
        hyscore_out_dict["proc_param"] = {
            "pulse_program": self.eprdata.pulse_program,
            "zf": self.zf,
            "poly_order": self.poly_order,
            "x_max": self.x_max,
            "x_units": "MHz",
            "y_units": "MHz",
            "workflow_type": "hyscore",
        }

        hyscore_out_dict["raw_data"] = self.eprdata.data
        x, y = self.eprdata.x, self.eprdata.y
        hyscore_out_dict["x_raw"],hyscore_out_dict["y_raw"] = x,y
        real_data = self.eprdata.data.real

            
        vprint(f"Baseline correction in dimension 1 with polynomial of order {self.poly_order}...")
        # baseline correction
        bc_data1, bc1 = _baseline_correct_2d(
            x,
            real_data,
            interactive=False,
            npts=x.size,
            method="polynomial",
            order=self.poly_order,
        )

        vprint(f"Baseline correction in dimension 2 with polynomial of order {self.poly_order}...")
        hyscore_out_dict["baseline_dim1"] = bc1
        bc_data2, bc2 = _baseline_correct_2d(
            y,
            bc_data1.T,
            interactive=False,
            npts=y.size,
            method="polynomial",
            order=self.poly_order,
        )
        hyscore_out_dict["baseline_dim2"] = bc2
        hyscore_out_dict["bc_data"] = bc_data2.T

        # windowing
        window1 = _hamming_window(x, x_max=self.x_max)
        window2 = _hamming_window(y, x_max=self.x_max)
        vprint(f"Applying Hamming window in dimension 1...")
        bc_w_data1 = hyscore_out_dict["bc_data"] * window1
        vprint(f"Applying Hamming window in dimension 2...")
        bc_w_data2 = bc_w_data1.T * window2
        hyscore_out_dict["bc_w_data"] = bc_w_data2.T
        hyscore_out_dict["window_dim1"] = window1
        hyscore_out_dict["window_dim2"] = window2

       
        if self.zf[-1] != 0:
            vprint(f"Zero filling {self.zf[-1]} points dimension 1 and 2...")
            x_spacing, y_spacing = np.mean(np.diff(x)), np.mean(np.diff(y))
            zf_x = np.linspace(
                x[0], x[-1] + (self.zf[-1] * x_spacing), x.size + self.zf[-1]
            )
            zf_y = np.linspace(
                y[0], y[-1] + (self.zf[-1] * y_spacing), y.size + self.zf[-1]
            )
            hyscore_out_dict["time_axis1"] = zf_x
            hyscore_out_dict["time_axis2"] = zf_y
            hyscore_out_dict["bc_w_zf_data"] = np.pad(
                hyscore_out_dict["bc_w_data"], self.zf
            )
        else:
            vprint(f"Skipped zero filling...")
            hyscore_out_dict["time_axis1"] = x
            hyscore_out_dict["time_axis2"] = y
            hyscore_out_dict["bc_w_zf_data"] = hyscore_out_dict["bc_w_data"]

        # 2DFFT
        vprint(f"Generating frequency axes...")
        hyscore_out_dict["frequency_axis1"] = _generate_freq_axis(
            self.eprdata, hyscore_out_dict["time_axis1"]
        )
        hyscore_out_dict["frequency_axis2"] = _generate_freq_axis(
            self.eprdata, hyscore_out_dict["time_axis2"]
        )

        # fft
        vprint(f"2D Fourier transformation...")
        hyscore_out_dict["FFT_data"] = np.fft.fft2(hyscore_out_dict["bc_w_zf_data"])
        hyscore_out_dict["FFT_shifted_data"] = np.fft.fftshift(
            hyscore_out_dict["FFT_data"]
        )
        bc_w_zf_fft_data_shifted_abs = np.absolute(hyscore_out_dict["FFT_shifted_data"])

        ## symmetrise
        if self.symmetrise is not False:
            if self.symmetrise == 'diag':
                vprint(f"Symmetrising along the diagonal...")
                bc_w_zf_fft_data_shifted_abs = np.sqrt(bc_w_zf_fft_data_shifted_abs*bc_w_zf_fft_data_shifted_abs.T)
            elif self.symmetrise  == 'antidiag':
                vprint(f"Symmetrising along the antidiagonal...")
                bc_w_zf_fft_data_shifted_abs = np.fliplr(np.sqrt(np.fliplr(bc_w_zf_fft_data_shifted_abs)*(np.fliplr(bc_w_zf_fft_data_shifted_abs).T)))
            else:
                vprint(f"Symmetrising along the diagonal and the antidiagonal...")
                bc_w_zf_fft_data_shifted_abs = np.sqrt(bc_w_zf_fft_data_shifted_abs*bc_w_zf_fft_data_shifted_abs.T)
                bc_w_zf_fft_data_shifted_abs = np.fliplr(np.sqrt(np.fliplr(bc_w_zf_fft_data_shifted_abs)*(np.fliplr(bc_w_zf_fft_data_shifted_abs).T)))

        # output as dict
        hyscore_out_dict["data"] = (
            bc_w_zf_fft_data_shifted_abs  # replace original data with processed data
        )
        hyscore_out_dict["dims"] = [
            hyscore_out_dict["frequency_axis2"],
            hyscore_out_dict["frequency_axis1"],
        ]
        hyscore_out_dict["is_complex"] = False
        hyscore_out_dict["history"].append(
            [f"Processed HYSCORE dataset from {hyscore_out_dict['filepath']}"]
        )
        vprint(f"Completed in {(time.time()-start_time):.2f} seconds.")
        return hyscore_out_dict

    def eseem(self):
        """
        Processes an ESEEM (Electron Spin Echo Envelope Modulation) EPR dataset with baseline correction, windowing, zero-filling, and 1D FFT.

        This workflow is designed for datasets acquired with ESEEM pulse programs, including:
        '2P ESEEM', '3P ESEEM', '2P ESEEM vs. B0', '3P ESEEM vs. B0', and '3P ESEEM vs tau'.
        It performs the following steps:
        - Checks if the pulse program matches supported ESEEM types and validates data dimensionality.
        - Stores processing parameters in the output dictionary.
        - Applies baseline correction using either exponential decay or polynomial fitting, depending on the pulse program and data dimensionality.
        - Applies a Hamming window function to the data.
        - Optionally zero-fills the data if specified.
        - Computes the time axis (zero-filled if specified).
        - Generates the frequency axis for FFT.
        - Performs a 1D FFT (or along the last axis for 2D data) and shifts the result.
        - Stores the absolute value of the shifted FFT as the processed data.
        - Updates the output dictionary with all intermediate and final results, including processing history.

        Returns
        -------
        dict
            A dictionary containing the processed ESEEM dataset, including:
            - 'proc_param': Processing parameters used.
            - 'raw_data': Original raw data.
            - 'baseline_dim1': Baseline correction results.
            - 'bc_data': Baseline-corrected data.
            - 'window_dim1': Window function applied.
            - 'bc_w_data': Baseline-corrected and windowed data.
            - 'time_axis1': Time axis (zero-filled if specified).
            - 'bc_w_zf_data': Zero-filled, baseline-corrected, windowed data.
            - 'frequency_axis1': Frequency axis for FFT.
            - 'FFT_data': FFT of processed data.
            - 'FFT_shifted_data': FFT data after shift.
            - 'data': Absolute value of shifted FFT (final processed data).
            - 'dims': Frequency axis (and second axis if 2D).
            - 'is_complex': Boolean indicating if data is complex (always False).
            - 'history': List of processing steps.
        """

        vprint = print if self.verbose is True else lambda *args, **kwargs: None
        start_time = time.time()

        if self.eprdata.pulse_program in ["2P ESEEM", "3P ESEEM"]:
            assert self.eprdata.data.ndim == 1, (
                f"Pulse program is {self.eprdata.pulse_program} but data dimension is {self.eprdata.data.ndim}"
            )
        elif self.eprdata.pulse_program in [
            "2P ESEEM vs. B0",
            "3P ESEEM vs. B0",
            "3P ESEEM vs tau",
        ]:
            assert self.eprdata.data.ndim == 2, (
                f"Pulse program is {self.eprdata.pulse_program} but data dimension is {self.eprdata.data.ndim}"
            )
        else:
            raise ValueError(f"Unknown pulse program : {self.eprdata.pulse_program}")
        
        vprint("Starting ESEEM workflow...")
        
        eseem_out_dict = self.eprdata.data_dict
        eseem_out_dict["proc_param"] = {
            "pulse_program": self.eprdata.pulse_program,
            "zf": self.zf,
            "poly_order": self.poly_order,
            "x_max": self.x_max,
            "x_units": "MHz",
            "workflow_type": self.eprdata.pulse_program,
        }

        eseem_out_dict["raw_data"] = self.eprdata.data
        x = self.eprdata.x
        eseem_out_dict["x_raw"] = x
        real_data = self.eprdata.data.real

        vprint(f"Detected pulse program : {self.eprdata.pulse_program}")

        # background correction
        if self.eprdata.data.ndim == 1:
            if self.eprdata.pulse_program == "2P ESEEM":
                vprint(f"Baseline correction using an exponential decay function...")
                bc_data, baseline = _baseline_correct_1d(
                    x,
                    real_data,
                    method="exponential_decay",
                    fit_eseem_max=self.pick_eseem_points,
                    npts=0,
                )
            elif self.eprdata.pulse_program == "3P ESEEM":
                vprint(f"Baseline correction in dimension 1 with polynomial of order {self.poly_order}...")
                bc_data, baseline = _baseline_correct_1d(
                    x, real_data, method="polynomial", npts=0, order=self.poly_order
                )
            else:
                raise ValueError(f"Unknown pulse program : {self.eprdata.pulse_program}")

            eseem_out_dict["baseline_dim1"] = baseline

        elif self.eprdata.data.ndim == 2:
            if self.eprdata.pulse_program == "2P ESEEM vs. B0":
                vprint(f"Baseline correction using an exponential decay function...")
                bc_data, baselines = _baseline_correct_2d(
                    x,
                    real_data,
                    method="exponential_decay",
                    fit_eseem_max=self.pick_eseem_points,
                    npts=0,
                )
            elif (
                self.eprdata.pulse_program == "3P ESEEM vs. B0"
                or self.eprdata.pulse_program == "3P ESEEM vs tau"
            ):
                vprint(f"Baseline correction in dimension 1 with polynomial of order {self.poly_order}...")
                bc_data, baselines = _baseline_correct_2d(
                    x, real_data, method="polynomial", npts=0, order=self.poly_order
                )
            else:
                raise ValueError(f"Unknown pulse program : {self.eprdata.pulse_program}")

            eseem_out_dict["baseline_dim1"] = baselines

        eseem_out_dict["bc_data"] = bc_data

        # windowing
        vprint(f"Applying Hamming window along dimension 1...")
        window = _hamming_window(x, x_max=self.x_max)
        bc_w_data = bc_data * window
        eseem_out_dict["window_dim1"] = window
        eseem_out_dict["bc_w_data"] = bc_w_data

        # zero filling
        if self.zf[-1] != 0:
            vprint(f"Zero filling {self.zf[-1]} points...")
            x_spacing = np.mean(np.diff(x))
            zf_x = np.linspace(
                x[0], x[-1] + (self.zf[-1] * x_spacing), x.size + self.zf[-1]
            )
            eseem_out_dict["time_axis1"] = zf_x

            if self.eprdata.data.ndim == 1:
                bc_w_zf_data = np.pad(
                    bc_w_data, pad_width=self.zf, mode="constant", constant_values=0
                )
            elif self.eprdata.data.ndim == 2:
                bc_w_zf_data = np.pad(
                    bc_w_data,
                    pad_width=((0, 0), self.zf),
                    mode="constant",
                    constant_values=0,
                )
        else:
            vprint(f"Skipping zero filling...")
            eseem_out_dict["time_axis1"] = x
            bc_w_zf_data = bc_w_data

        eseem_out_dict["bc_w_zf_data"] = bc_w_zf_data

        # FFT
        vprint(f"Generating frequency axes...")
        frequency_axis1 = _generate_freq_axis(self.eprdata,eseem_out_dict["time_axis1"])

        # fft shift
        vprint(f"Fourier transformation...")
        bc_w_zf_fft_data = np.fft.fft(bc_w_zf_data, axis=-1)
        bc_w_zf_fft_data_shifted = np.fft.fftshift(bc_w_zf_fft_data)
        bc_w_zf_fft_data_shifted_abs = np.absolute(bc_w_zf_fft_data_shifted)

        # output as dict
        eseem_out_dict["frequency_axis1"] = frequency_axis1
        eseem_out_dict["FFT_data"] = bc_w_zf_fft_data
        eseem_out_dict["FFT_shifted_data"] = bc_w_zf_fft_data_shifted
        eseem_out_dict["data"] = bc_w_zf_fft_data_shifted_abs
        eseem_out_dict["dims"] = (
            [frequency_axis1]
            if self.eprdata.y is None
            else [self.eprdata.y, frequency_axis1]
        )
        eseem_out_dict["is_complex"] = False
        eseem_out_dict["history"].append(
            [f"Processed ESEEM dataset from {eseem_out_dict['filepath']}"]
        )
        vprint(f"Completed in {(time.time()-start_time):.2f} seconds.")

        return eseem_out_dict
