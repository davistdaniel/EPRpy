import numpy as np
from datetime import datetime
from copy import deepcopy


def eprscale_between(eprdata,min_val=None,max_val=None):

    min_val = 0 if min_val is None else min_val
    max_val = 1 if max_val is None else max_val

    data_min = np.min(eprdata.data,axis=-1)
    data_max = np.max(eprdata.data,axis=-1)

    eprdata.data = (eprdata.data-data_min)/(data_max-data_min)
    eprdata.data *= int(max_val-min_val)
    eprdata.data += min_val

    eprdata.history.append([f'{str(datetime.now())} : Data scaled between {min_val} and {max_val}.',deepcopy(eprdata)])


def eprintegrate(eprdata):

    delta_B = np.mean(np.diff,eprdata.x)
    integral = np.cumsum(eprdata.data,axis=-1)*delta_B 

    eprdata.data = integral
    eprdata.history.append([f'{str(datetime.now())} : Integral calculated',deepcopy(eprdata)])