import numpy as np
import re
import warnings
from datetime import datetime
from pathlib import Path
from copy import deepcopy

from eprpy.plotter import eprplot
from eprpy.processor import _integrate,_scale_between,_baseline_correct


def load(filepath):
    """This function reads EPR experiment files from Bruker spectrometer file format (BES3T 1.2).

    Parameters
    ----------
    filepath : str
        A filepath which points to either .DSC or .DTA file

    Returns
    -------
    out_dict : dict
        A dictionary containing differente keys
    """

    out_dict = {'dims':None,
                'data':None,
                'acq_param':None}

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
    """Gets data type of data stored in .DTA by using the byteorder and data format specified in the .DSC file.

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
        raise ValueError(f'IRFMT keyword, which specifies the format of real values, could not be read from .DSC file.')
    
    # get the byteorder, BIG for big endian, LIT for little endian
    if 'BSEQ' in dsc_parameter_dict:
        byteorder_dict = {'BIG':'>','LIT':'<'}
        data_byteorder = byteorder_dict[dsc_parameter_dict['BSEQ']]
    else:
        raise ValueError('BSEQ keyword, which specifies the byte order of data, could not be read from the .DSC file.')

    data_type = data_byteorder+data_format_real

    return np.dtype(data_type),data_is_complex

def get_dim_arrays(dsc_parameter_dict,dta_filepath):
    
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
        raise FileNotFoundError(f'{ax_name}GF was not found at {str(dta_filepath.parent)}')
    
    return gf_data


class EprData():
    
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
        self.history[0].append(deepcopy(self))

    
    def plot(self,g_scale=False,plot_type='stacked', slices='all', spacing=0.5,plot_imag=True):

        eprplot(self,plot_type,slices,spacing,plot_imag,g_scale=g_scale)

    def scale_between(self,min_val=None,max_val=None):

        _scale_between(self,min_val,max_val)

    def integral(self):
        
        _integrate(self)

    def baseline_correction(eprdata,interactive=False,
                      npts=10,method='linear',spline_smooth=1e-5,
                      order=2):
        
        _baseline_correct(eprdata,interactive,
                          npts,method,spline_smooth,order)
        
    def select_region(self,region):


        assert type(region) in [range,list],'region keyword must be a range object or list.'
        out_dict = deepcopy(self.data_dict)
        out_dict['dims'][-1] =  out_dict['dims'][-1][region]
        out_dict['data'] =  out_dict['data'][...,region]

        return EprData(out_dict)
    
    def undo(self):
        """
        Undo the processing step done on an EprData object by returning the previous EprData object.

        Returns
        -------
        EprData
            Returns the last-saved EprData object from EprData.history
        """

        return self.history[-1][1]

        
        
