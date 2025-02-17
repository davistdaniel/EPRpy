from pathlib import Path
import sys
import pytest
import numpy as np

from eprpy.loader import check_filepaths,read_DSC_file,get_dim_arrays,get_DTA_datatype,read_DTA_file,read_GF_file
import eprpy as epr

current_dir = Path(__file__).resolve().parent
data_dir = str(current_dir / 'data')
python_version = sys.version_info  

@pytest.fixture
def test_load_1d():
    epr_1d_data = epr.load(data_dir+'/tempo.DSC')
    return epr_1d_data

@pytest.fixture
def test_load_2d():
    epr_2d_data = epr.load(data_dir+'/tempo_time.DSC')
    return epr_2d_data

def test_check_filepaths():
    test_filepath_dsc = data_dir+'/tempo.DSC'
    test_filepath_dta = data_dir+'/tempo.DTA'


    dta_filepath,dsc_filepath = check_filepaths(test_filepath_dsc)
    dta_filepath1,dsc_filepath1 = check_filepaths(test_filepath_dta)

    assert dta_filepath.parts[-1] == 'tempo.DTA'
    assert dsc_filepath.parts[-1] == 'tempo.DSC'
    assert dta_filepath1.parts[-1] == 'tempo.DTA'
    assert dsc_filepath1.parts[-1] == 'tempo.DSC'

    with pytest.raises(FileNotFoundError):
        test_filepath_dsc = str(data_dir)+'/tempo1.DSC'
        dta_filepath,dsc_filepath = check_filepaths(test_filepath_dsc)
    with pytest.raises(FileNotFoundError):
        test_filepath_dta = str(data_dir)+'/tempo1.DTA'
        dta_filepath,dsc_filepath = check_filepaths(test_filepath_dta)

def test_read_DSC_file():
    test_filepath_dsc = data_dir+'/tempo.DSC'

    exp_dict = {'DSRC': 'EXP','BSEQ': 'BIG','IKKF': 'REAL','XTYP': 'IDX','YTYP': 'NODATA','ZTYP': 'NODATA','IRFMT': 'D',
    'XPTS': 2048,'XMIN': 3259.75,'XWID': 130.136426,'TITL': 'tempo','IRNAM': 'Intensity','XNAM': 'Field','IRUNI': '','XUNI': 'G',
    'OPER': 'xuser','DATE': '12/03/20','TIME': '10:57:45','STAG': 'C','EXPT': 'CW','OXS1': 'IADC','AXS1': 'B0VL','AXS2': 'NONE',
    'A1CT': 0.332485,'A1SW': 0.01302,'MWFQ': '9.327654e+09','MWPW': 0.002,'AVGS': 109,'SPTP': 0.03,'RCAG': 60,'RCHM': 1,'B0MA': '4e-05',
    'B0MF': 100000,'RCPH': 0.0,'RCOF': 0.0,'A1RS': 2048,'RCTC': 0,'AllegroMode': 'True','CenterField': '3324.85 G','Delay': '0.0 s','FieldFlyback': 'On',
    'FieldWait': 'Wait LED off','GFactor': 2.0,'MeasuringHall': 'False','SetToSampleG': 'False','StaticFieldMon': '3480.000 G','SweepDirection': 'Up',
    'SweepWidth': '130.2 G','WidthTM': '200.0 G','FrequencyMon': '9.327654 GHz','QMonitBridge': 'On','AcqFineTuning': 'Never','AcqScanFTuning': 'Off',
    'AcqSliceFTuning': 'Off','BridgeCalib': 60.0,'Power': '2.000 mW','PowerAtten': '20.0 dB','BaselineCorr': 'Off','NbScansAcc': 109,'NbScansDone': 109,
    'NbScansToDo': 200,'ReplaceMode': 'Off','SmoothMode': 'Manual','SmoothPoints': 1,'AFCTrap': 'True','AllowShortCt': 'False','Calibrated': 'True','ConvTime': '30.00 ms',
    'DModDetectSCT': 'First','DoubleModAcc': 1,'DoubleModFreq': '5.000 kHz','DoubleMode': 'False','DualDetect': 'OFF','EliDelay': '1.0 us',
    'Enable1stHarm': 'True','Enable1stHarm90': 'False','Enable2ndHarm': 'False','Enable2ndHarm90': 'False','Enable3rdHarm': 'False','Enable3rdHarm90': 'False',
    'Enable4thHarm': 'False','Enable4thHarm90': 'False','Enable5thHarm': 'False','Enable5thHarm90': 'False','EnableDisp': 'False','EnableImag': 'Disable','ExtLockIn': 'False',
    'ExtTrigger': 'False','Gain': '60 dB','GainB': '60 dB','Harmonic': 1,'HighPass': 'True','InputPlugA': 'AC3','InputPlugB': 'AC3','Integrator': 'False','IsCalibExp': 'False',
    'ModAmp': '0.400 G','ModFreq': '100.00 kHz','ModPhase': 0.0,'Offset': '0.0 %','QuadMode': 'False','Resolution': 2048,'Resonator': 1,'SctNorm': 'True',
    'SctRevision': 'Allegro','SetAllOrd': 'False','SetOrdDef': 'False','SpuExtension': 'True','SpuRevision': 'MultiHarmonic',
    'SweepTime': '61.44000 s','TimeConst': 0,'TimeExp': 'False','TuneCaps': 45,'dModSW': 'True'}
    
    assert exp_dict==read_DSC_file(Path(test_filepath_dsc))


def test_get_dim_arrays():
    test_filepath_dsc = data_dir+'/tempo.DSC'
    test_filepath_dta = data_dir+'/tempo.DTA'
    test_dsc_dict = read_DSC_file(Path(test_filepath_dsc))
    exp_dim = np.load(data_dir+'/test_get_dim_array.npy')

    test_ntup,test_dim = get_dim_arrays(test_dsc_dict,Path(test_filepath_dta))
    
    assert test_ntup == (1, 1, 2048)
    np.testing.assert_array_almost_equal(exp_dim,test_dim)

def test_get_DTA_datatype():
    test_filepath_dsc = data_dir+'/tempo.DSC'
    test_dsc_dict = read_DSC_file(Path(test_filepath_dsc))

    assert get_DTA_datatype(test_dsc_dict) == (np.dtype('>f8'), False)

def test_read_DTA_file():
    test_filepath_dsc = data_dir+'/tempo.DSC'
    test_filepath_dta = data_dir+'/tempo.DTA'
    test_dsc_dict = read_DSC_file(Path(test_filepath_dsc))

    exp_datadata = np.load(data_dir+'/test_read_dta_file_data.npy')
    exp_dimlist0 = np.load(data_dir+'/test_read_dta_file_dimlist0.npy')

    test_datadta,test_dimlist = read_DTA_file(Path(test_filepath_dta),test_dsc_dict)
    
    np.testing.assert_array_almost_equal(exp_datadata,test_datadta)
    np.testing.assert_array_almost_equal(test_dimlist[0],exp_dimlist0)
    assert isinstance(test_dimlist,list)

def test_read_GF_file():
    test_filepath_dsc = data_dir+'/tempo.DSC'
    test_filepath_dta = data_dir+'/tempo.DTA'
    test_dsc_dict = read_DSC_file(Path(test_filepath_dsc))

    with pytest.raises(FileNotFoundError):
        _ = read_GF_file('Y',test_dsc_dict,Path(test_filepath_dta))
    

    test_filepath_dsc = data_dir+'/tempo_time.DSC'
    test_filepath_dta = data_dir+'/tempo_time.DTA'
    test_dsc_dict = read_DSC_file(Path(test_filepath_dsc))
    exp_gf_data = np.load(data_dir+'/test_read_GF_file_data.npy')

    np.testing.assert_array_almost_equal(exp_gf_data,read_GF_file('Y',test_dsc_dict,Path(test_filepath_dta)))

    with pytest.raises(FileNotFoundError):
        _ = read_GF_file('X',test_dsc_dict,Path(test_filepath_dta))

def test_load_error():
    with pytest.raises(FileNotFoundError):
        _ = epr.load(data_dir+'/tempo1.DSC')

class TestEPR1d():
    def test_load_1d_epr(self,test_load_1d):

        assert type(test_load_1d) is epr.loader.EprData
        assert test_load_1d.y is None

        exp_x = np.load(data_dir+'/test_load_1d_epr_x.npy')
        exp_data = np.load(data_dir+'/test_load_1d_epr.npy')

        np.testing.assert_array_almost_equal(exp_x,test_load_1d.x)
        np.testing.assert_array_almost_equal(exp_data,test_load_1d.data)

        test_filepath_dsc = data_dir+'/tempo.DSC'
        test_dsc_dict = read_DSC_file(Path(test_filepath_dsc))

        assert test_dsc_dict == test_load_1d.acq_param
        assert test_load_1d.is_complex is False
        assert test_load_1d.filepath == test_filepath_dsc

    def test_scale_between(self,test_load_1d):

        exp_data = np.load(data_dir+'/test_scale_between1d_default.npy')
        np.testing.assert_array_almost_equal(test_load_1d.scale_between().data,exp_data)

        exp_data = np.load(data_dir+'/test_scale_between1d-1_1.npy')
        np.testing.assert_array_almost_equal(test_load_1d.scale_between(-1,1).data,exp_data)

    def test_integral(self,test_load_1d):

        exp_data = np.load(data_dir+'/test_integral.npy')
        np.testing.assert_array_almost_equal(test_load_1d.integral().data,exp_data)

    def test_baseline_correction(self,test_load_1d):

        exp_data = np.load(data_dir+'/test_default_bc.npy')
        np.testing.assert_array_almost_equal(test_load_1d.baseline_correct().data,exp_data)

        exp_data = np.load(data_dir+'/test_poly2_bc.npy')
        np.testing.assert_array_almost_equal(test_load_1d.baseline_correct(method='polynomial',order=2).data,exp_data)

        exp_data = np.load(data_dir+'/test_poly2_bc_baseline.npy')
        np.testing.assert_array_almost_equal(test_load_1d.baseline_correct(method='polynomial',order=2).baseline,exp_data)

        exp_data = np.load(data_dir+'/test_spline_bc.npy')
        np.testing.assert_array_almost_equal(test_load_1d.baseline_correct(method='spline').data,exp_data)

        exp_data = np.load(data_dir+'/test_spline_bc_baseline.npy')
        np.testing.assert_array_almost_equal(test_load_1d.baseline_correct(method='spline').baseline,exp_data)

    def test_plot(self,test_load_1d):
        fig,ax=test_load_1d.plot()
        fig.savefig(data_dir+'/test_results/1dplot.png')

class TestEPR2d():

    def test_load_2d_epr(self,test_load_2d):

        assert type(test_load_2d) is epr.loader.EprData
        assert test_load_2d.y is not None

        exp_x = np.load(data_dir+'/test_load_2d_epr_x.npy')
        exp_data = np.load(data_dir+'/test_load_2d_epr.npy')
        exp_y = np.load(data_dir+'/test_load_2d_epr_y.npy')

        np.testing.assert_array_almost_equal(exp_x,test_load_2d.x)
        np.testing.assert_array_almost_equal(exp_y,test_load_2d.y)
        np.testing.assert_array_almost_equal(exp_data,test_load_2d.data)

        test_filepath_dsc = data_dir+'/tempo_time.DSC'
        test_dsc_dict = read_DSC_file(Path(test_filepath_dsc))

        assert test_dsc_dict == test_load_2d.acq_param
        assert test_load_2d.is_complex is False
        assert test_load_2d.filepath == test_filepath_dsc

    def test_scale_between(self,test_load_2d):

        exp_data = np.load(data_dir+'/test_scale_between2d_default.npy')
        np.testing.assert_array_almost_equal(test_load_2d.scale_between().data,exp_data)

    def test_baseline_correction(self,test_load_2d):

        exp_data = np.load(data_dir+'/test_default2d_bc.npy')
        np.testing.assert_array_almost_equal(test_load_2d.baseline_correct().data,exp_data)

    def test_plot(self,test_load_2d):
        fig,ax=test_load_2d.plot()
        fig.savefig(data_dir+'/test_results/2dplot.png')

        fig,ax=test_load_2d.plot(slices=range(0,20))
        fig.savefig(data_dir+'/test_results/2dplot_range.png')
        
        fig,ax=test_load_2d.plot(plot_type='superimposed')
        fig.savefig(data_dir+'/test_results/2dplot_superimposed.png')
        
        fig,ax=test_load_2d.plot(plot_type='pcolor')
        fig.savefig(data_dir+'/test_results/2dplot_pcolor.png')
        
        fig,ax=test_load_2d.plot(plot_type='surf')
        fig.savefig(data_dir+'/test_results/2dplot_surf.png')