import numpy as np
import re
import warnings
from datetime import datetime
from pathlib import Path
from copy import deepcopy

# EPRpy
from eprpy.plotter import eprplot
from eprpy.processor import _integrate,_scale_between,_baseline_correct,_derivative
from eprpy.workflows import EprWorkflow

warnings.simplefilter("always")

def load(filepath):

    """
    Load EPR experiment files from the Bruker spectrometer file format (BES3T 1.2).

    Parameters
    ----------
    filepath : str
        The path to a .DSC or .DTA file containing EPR experimental data.

    Returns
    -------
    EprData
        An instance of the `EprData` class.

    Notes
    -----
    - The returned `EprData` object includes attributes such as:
        - `filepath`: The input file path.
        - `dims`: A list of dimensions of the data.
        - `data`: The experimental data, either real or complex.
        - `acq_param`: A dictionary of acquisition parameters.
        - `is_complex`: Boolean indicating if the data is complex.
        - `history`: A log of actions performed on the data, initialized with a load entry.
    """

    out_dict = {'dims':None,
                'data':None,
                'acq_param':None,
                'workflow_type':None}

    dta_filepath,dsc_filepath = check_filepaths(filepath)
    dsc_parameter_dict = read_DSC_file(dsc_filepath)
    out_data,dim_list = read_DTA_file(dta_filepath,dsc_parameter_dict)

    out_dict['filepath'] = filepath
    out_dict['dims'] = dim_list
    out_dict['data'] = out_data
    out_dict['acq_param'] = dsc_parameter_dict
    out_dict['is_complex'] = np.iscomplexobj(out_data)
    out_dict['history'] = [[f'{str(datetime.now())} : Data loaded from {filepath}.']]

    return EprData(out_dict)

def check_filepaths(filepath):
    """This function checks if the filepath is valid and generates DSC and DTA filepaths.

    Parameters
    ----------
    filepath : str
        Filepath to .DSC or .DTA file.

    Returns
    -------
    Path
        DTA and DSC filepaths as a Path object.

    Raises
    ------
    ValueError
        If filepath does not point to .DSC or .DTA file.
    FileNotFoundError
        If filepath is not found.
    FileNotFoundError
        If DTA filepath is not found.
    FileNotFoundError
        If DSC filepath is not found.
    """
    # convert to a Path
    filepath_temp = Path(filepath)

    # check if DTA or DSC filepath was given
    if filepath_temp.exists():
        if filepath_temp.suffix == '.DSC':
            DTA_filepath = filepath_temp.with_suffix('.DTA')
            DSC_filepath = filepath_temp
        elif filepath_temp.suffix == '.DTA':
            DSC_filepath = filepath_temp.with_suffix('.DSC')
            DTA_filepath = filepath_temp
        else:
            raise ValueError('Filepath must point to a .DSC or .DTA file, not : {filepath}')
    else:
        raise FileNotFoundError(f'File does not exist at : {filepath}')
    
    # check if DTA and DSC filepaths are valid.
    if not DTA_filepath.exists():
        raise FileNotFoundError(f'DTA file does not exist at : {str(filepath_temp.parent)}')
    if not DSC_filepath.exists():
        raise FileNotFoundError(f'DSC file does not exist at : {str(filepath_temp.parent)}')
    
    return DTA_filepath,DSC_filepath

def read_DSC_file(dsc_filepath):

    """
    Read and parse a DSC file from a Bruker EPR spectrometer.

    Parameters
    ----------
    dsc_filepath : str
        The file path to the `.DSC` file containing acquisition parameters.

    Returns
    -------
    parameter_dict : dict
        A dictionary containing the parameters and their corresponding values extracted 
        from the DSC file.

    Notes
    -----
    - The function reads each line of the `.DSC` file and extracts parameter-value pairs.
    - Lines starting with `*` or blank lines are ignored as comments. 
    - Parameters are stored as keys in the dictionary, and their values are converted 
      to appropriate types:
        - Numeric values are stored as `int` or `float`.
        - Text values enclosed in single quotes are stored as `str`.
    """

    parameter_dict = {}

    with open(dsc_filepath,'r') as dsc_file:
        for line in dsc_file:
            line = line.strip()
            
            # Skip lines which start with *, comments
            if not line or line.startswith('*'):
                continue
            
            # find parameters and values
            param_val_pair = re.match(r'(\w+)\s+(.*)', line)
            if param_val_pair:
                parameter,value = param_val_pair.groups()
                if re.match(r'^-?\d+\.?\d*$', value): # store numeric value as float or int
                    value = float(value) if '.' in value else int(value)
                elif re.match(r"^'.*'$", value): #store text as str
                    value = value.strip("'")
                
                parameter_dict[parameter] = value
    
    return parameter_dict

def read_DTA_file(dta_filepath,dsc_parameter_dict):

    """
    Read and parse a DTA file from a Bruker EPR spectrometer.

    Parameters
    ----------
    dta_filepath : str
        The file path to the `.DTA` file containing binary EPR data.
    dsc_parameter_dict : dict
        A dictionary of acquisition parameters extracted from the corresponding `.DSC` file.

    Returns
    -------
    out_data : ndarray
        The processed data from the `.DTA` file, reshaped according to the acquisition 
        parameters and returned as a NumPy array. If the data is complex, it combines 
        real and imaginary parts.
    dim_list : list
        A list of dimension arrays that describe the shape of the data.

    Notes
    -----
    - Binary data is read from the `.DTA` file and separated into real and imaginary 
      components if the data is complex.
    - The data is reshaped into the dimensions specified in the acquisition parameters.

    """

    ## get data type
    data_type,data_is_complex = get_DTA_datatype(dsc_parameter_dict)

    ## read binary DTA file
    with open(dta_filepath) as dta_file:
        data = np.fromfile(dta_file,dtype=data_type)
    
    # seaprate data into real_data and imag data
    if data_is_complex:
        real_data = data[0::2]
        imag_data = data[1::2]
    else:
        real_data = data
        imag_data = None

    npts_tup,dim_list = get_dim_arrays(dsc_parameter_dict,dta_filepath)

    if data_is_complex:
        real_data = real_data.reshape(npts_tup)
        imag_data = imag_data.reshape(npts_tup)
        out_data = real_data+1j*imag_data
    else:
        out_data = real_data.reshape(npts_tup)

    return np.squeeze(out_data),dim_list

def get_DTA_datatype(dsc_parameter_dict):
    
    """
    Gets data type of data stored in .DTA by using the byteorder and data format specified in the .DSC file.

    Parameters
    ----------
    dsc_parameter_dict : dict
        A dictionary containing paraemters and values obtained from .DSC file

    Returns
    -------
    datatype
        np.dtype object

    Raises
    ------
    ValueError
        If 'IRFMT' keyword is not found.
    ValueError
        If 'BSEQ' keyword is not found.
    """

    # check if data is complex
    if 'IKKF' in dsc_parameter_dict:
        data_is_complex = True if dsc_parameter_dict['IKKF']=='CPLX' else False
    else:
        warnings.warn('IKKF keyword was not read from .DSC file, assuming data is real.')
        data_is_complex = False

    # define real datatype from IRFMT keyword
    if 'IRFMT' in dsc_parameter_dict:
        data_format_dict = {'C':'i1','S':'i2','I':'i4','F':'f4','D':'f8'}
        data_format_real = data_format_dict[dsc_parameter_dict['IRFMT']]
    else:
        raise ValueError('IRFMT keyword, which specifies the format of real values, could not be read from .DSC file.')
    
    # get the byteorder, BIG for big endian, LIT for little endian
    if 'BSEQ' in dsc_parameter_dict:
        byteorder_dict = {'BIG':'>','LIT':'<'}
        data_byteorder = byteorder_dict[dsc_parameter_dict['BSEQ']]
    else:
        raise ValueError('BSEQ keyword, which specifies the byte order of data, could not be read from the .DSC file.')

    data_type = data_byteorder+data_format_real

    return np.dtype(data_type),data_is_complex

def get_dim_arrays(dsc_parameter_dict,dta_filepath):

    """
    Generate dimension arrays based on the acquisition parameters from a `.DSC` file.

    Parameters
    ----------
    dsc_parameter_dict : dict
        A dictionary containing acquisition parameters extracted from the `.DSC` file.
    dta_filepath : Path
        File path to the `.DTA` file, used to locate `.GF` files if needed.

    Returns
    -------
    npts_tup : tuple
        A tuple specifying the number of points along each dimension (Z, Y, X).
    dim_list : list
        A list of NumPy arrays representing the dimensions along each axis:
        - Z-axis
        - Y-axis
        - X-axis
    """
    
    # define axis lengths
    xpts,ypts,zpts = 1,1,1
    if 'XPTS' in dsc_parameter_dict:
        xpts = dsc_parameter_dict['XPTS']
    if 'YPTS' in dsc_parameter_dict:
        ypts = dsc_parameter_dict['YPTS']
    if 'ZPTS' in dsc_parameter_dict:
        zpts = dsc_parameter_dict['ZPTS']

    # get number of points in each dimension and genrate arrays along each dimension
    npts_tup = (zpts,ypts,xpts)
    dim_list = []
    
    axis_names = ['Z','Y','X']
    axis_types = [dsc_parameter_dict[axis_name+'TYP'] for idx,axis_name in enumerate(axis_names)]
    
    for idx,ax_typ in enumerate(axis_types):
        if npts_tup[idx]>1:
            if ax_typ=='IDX':
                ax_min = dsc_parameter_dict[axis_names[idx]+'MIN']
                ax_wid = dsc_parameter_dict[axis_names[idx]+'WID']
                dim_list.append(ax_min+np.linspace(0,ax_wid,npts_tup[idx]))
            elif ax_typ=='IGD':
                gf_data = read_GF_file(axis_names[idx],dsc_parameter_dict,dta_filepath)
                dim_list.append(gf_data)

    return npts_tup,dim_list

def read_GF_file(ax_name,dsc_parameter_dict,dta_filepath):

    """
    Read and parse a gradient field (GF) file associated with a Bruker EPR spectrometer.

    Parameters
    ----------
    ax_name : str
        The axis name (e.g., 'X', 'Y') for which the GF file is being read.
    dsc_parameter_dict : dict
        A dictionary of acquisition parameters extracted from the `.DSC` file.
    dta_filepath : Path
        The file path to the `.DTA` file, used to locate the corresponding `.GF` file.

    Returns
    -------
    gf_data : ndarray
        The data from the `.GF` file as a NumPy array.

    Raises
    ------
    ValueError
        If the data format for the axis cannot be determined from the `.DSC` file.
    FileNotFoundError
        If the `.GF` file corresponding to the specified axis does not exist.
    """

    data_format_dict = {'C':'i1','S':'i2','I':'i4','F':'f4','D':'f8'}
    byteorder_dict = {'BIG':'>','LIT':'<'}

    gf_filepath = dta_filepath.with_suffix('.'+ax_name+'GF')
    if gf_filepath.exists():
        if ax_name+'FMT' in dsc_parameter_dict:
            gf_dataformat = data_format_dict[dsc_parameter_dict[ax_name+'FMT']]
        else:
            raise ValueError(ax_name+f'FMT keyword, which specifies the format of {ax_name} axis, could not be read from .DSC fie')
        
        gf_byteorder = byteorder_dict[dsc_parameter_dict['BSEQ']]
        with open(gf_filepath,'rb') as gf_file:
            gf_data = np.fromfile(gf_file,dtype=np.dtype(gf_byteorder+gf_dataformat))
    else:
        raise FileNotFoundError(f'{ax_name}GF was not found at {str(gf_filepath)}')
    
    return gf_data


class EprData():

    """
    A class representing EPR data with methods for processing and visualization.

    Attributes
    ----------
    data_dict : dict
        The dictionary containing EPR data and metadata.
    filepath : str
        Path to the source file.
    data : ndarray
        The EPR data, possibly complex.
    dims : list
        Dimensions of the data (X, Y, Z axes).
    acq_param : dict
        Acquisition parameters from the experiment.
    is_complex : bool
        Indicates if the data is complex.
    history : list
        List of saved states for undo operations.
    x : ndarray
        X-axis data.
    y : ndarray or None
        Y-axis data if present.
    g : ndarray or None
        g-values if calculated.

    Methods
    -------
    plot(g_scale=False, plot_type='stacked', slices='all', spacing=0.5, plot_imag=True):
        Plots the EPR data.
    scale_between(min_val=None, max_val=None):
        Scales the data to a given range.
    integral():
        Integrates the EPR data.
    baseline_correction(interactive=False, npts=10, method='linear', spline_smooth=1e-5, order=2):
        Performs baseline correction on the data.
    select_region(region):
        Selects a specific region of the data.
    undo():
        Reverts to the previous state of the EprData object.
    """

    
    def __init__(self,out_dict):
        
        self.data_dict = out_dict
        self.filepath = out_dict['filepath']
        self.data = out_dict['data']
        self.dims = out_dict['dims']
        self.acq_param = out_dict['acq_param']
        self.is_complex = out_dict['is_complex']
        self.history = out_dict['history']
        self.x = self.dims[-1].copy()
        self.y = self.dims[-2].copy() if len(self.dims) >1 else None
        if self.acq_param['XNAM'] == 'Field':
            x_g = np.ma.masked_equal(self.x,0)
            self.g = ((float(self.acq_param['MWFQ'])/1e+9)/(13.996*(x_g/10000)))
        else:
            self.g = None
        self.workflow_type = out_dict['workflow_type']
        self.history[-1].append(deepcopy(self))

        if "PlsSPELEXPSlct" in self.acq_param:
            self.pulse_program = self.acq_param["PlsSPELEXPSlct"]
        else:
            self.pulse_program = "Unknown"

    
    def plot(self,g_scale=False,plot_type='stacked', slices='all', spacing=0.5,plot_imag=True,interactive=False):

        fig,ax = eprplot(self,plot_type,slices,spacing,plot_imag,g_scale=g_scale,interactive=interactive)
        return fig,ax

    def scale_between(self,min_val=None,max_val=None):

        eprdata_proc = _scale_between(self,min_val,max_val)
        return eprdata_proc

    def integral(self):
        
        eprdata_proc = _integrate(self)
        return eprdata_proc

    def baseline_correct(self,interactive=False, npts=0, method="linear", spline_smooth=1e-5, order=2,init_vals=None,bounds = (-np.inf, np.inf),fit_eseem_max=False):
        
        eprdata_proc = _baseline_correct(self,interactive, npts, method, spline_smooth, order,init_vals,bounds,fit_eseem_max)
        return eprdata_proc

        
    def select_region(self,region):

        assert type(region) in [range,list],'region keyword must be a range object or list.'
        out_dict = deepcopy(self.data_dict)
        out_dict['dims'][-1] =  out_dict['dims'][-1][region]
        out_dict['data'] =  out_dict['data'][...,region]

        return EprData(out_dict)
    
    def derivative(self,sigma=1,axis=-1):

        epr_data_proc = _derivative(self,sigma,axis)
        return epr_data_proc

    def workflow(self,zf=0,poly_order=3,x_max=None,pick_eseem_points=False,symmetrise=False,verbose=False):

        if self.pulse_program == "HYSCORE":
            hyscore_out_dict = EprWorkflow(eprdata=self,zf=zf,poly_order=poly_order,x_max=x_max,pick_eseem_points=pick_eseem_points,symmetrise=symmetrise,verbose=verbose).hyscore()
            return EprData(hyscore_out_dict)
        
        elif self.pulse_program in ["2P ESEEM", "3P ESEEM","2P ESEEM vs. B0","3P ESEEM vs. B0","3P ESEEM vs tau"]:
            eseem_out_dict = EprWorkflow(eprdata=self,zf=zf,poly_order=poly_order,x_max=x_max,pick_eseem_points=pick_eseem_points,verbose=verbose).eseem()
            return EprData(eseem_out_dict)
        
        else:
            raise ValueError(f"No supported workflows found for the pulse program : {self.pulse_program}")



