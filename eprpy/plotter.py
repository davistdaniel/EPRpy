import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.widgets import Button
import warnings
warnings.simplefilter('always')



color_cycle = plt.cm.tab10.colors[:10]

def eprplot(eprdata_list, plot_type='stacked', slices='all', spacing=0.5,plot_imag=True,g_scale=False):
    """
    Plot one or multiple EPR data objects for comparison.

    Parameters
    ----------
    eprdata_list : list
        List of eprdata objects, each with attributes:
            - filepath : str, path to the data file.
            - data : ndarray, can be 1D or 2D, real or complex.
            - acq_param : dict, acquisition parameters.
    
    plot_type : str, optional
        Type of plot for 2D data. Options are:
            'stacked' (default), 'superimposed', 'surf', or 'contour'.

    slices : str or list, optional
        Specifies which slices to plot if data is 2D. Options:
            'all' (default) for all slices, an integer list for specific slices, or a range.

    spacing : float, optional
        Spacing between slices for 'stacked' or 'superimposed' plots. Default is 0.5.

    Returns
    -------
    None
    """
    
    if not isinstance(eprdata_list, list):
        eprdata_list = [eprdata_list]  # Convert single object to a list for uniform handling
    
    if eprdata_list[0].data.ndim==1:
        assert all([i.data.ndim==1 for i in eprdata_list]), 'Only datasets with same number of dimensions can be compared.'
        ndim=1
    if eprdata_list[0].data.ndim==2:
        assert all([i.data.ndim==2 for i in eprdata_list]), 'Only datasets with same number of dimensions can be compared.'
        ndim=2

    if ndim==1:
        fig,ax = plot_1d(eprdata_list,g_scale,plot_imag)
    elif ndim==2:
        fig,ax = plot_2d(eprdata_list,g_scale,plot_type, slices, spacing)

    fig.tight_layout()
    if g_scale and eprdata_list[0].g is not None: 
        ax.invert_xaxis()
    
    plt.show()

    return fig,ax


def plot_1d(eprdata_list,g_scale,plot_imag=True):
    
    c_idx = -1

    # initiate plot
    fig,ax = plt.subplots()

    for idx, eprdata in enumerate(eprdata_list):

        if c_idx>=9:
            c_idx=-1
        c_idx+=1

        data = eprdata.data
        if g_scale:
            if eprdata.g is not None:
                x = eprdata.g
            else:
                x = eprdata.x
                warnings.warn('Unable to set g values as axis.')  
        else:
            x = eprdata.x

        if np.iscomplexobj(data):
            ax.plot(x,np.real(data), label=f'Real',color=color_cycle[c_idx])
            if plot_imag:
                ax.plot(x,np.imag(data), '--', alpha=0.5, label='Imaginary',color=color_cycle[c_idx])
        else:
            ax.plot(x,data, label='Real',color=color_cycle[c_idx])
    
    return fig,ax
        

def plot_2d(eprdata_list,g_scale,plot_type='stacked',slices='all', spacing=0.5):

    data = eprdata_list[0].data
    if g_scale:
        if eprdata_list[0].g is not None:
            x = eprdata_list[0].g
        else:
            x = eprdata_list[0].x
            warnings.warn('Unable to set g values as axis.')  
    else:
        x = eprdata_list[0].x
    y = eprdata_list[0].y
    num_slices, slice_len = data.shape

    # Select slices
    if slices == 'all':
        selected_slices = range(num_slices)
    elif isinstance(slices, list):
        selected_slices = [s for s in slices if 0 <= s < num_slices]
    elif isinstance(slices, range):
        selected_slices = [s for s in slices if 0 <= s < num_slices]
    else:
        raise ValueError("Invalid value for 'slices'. Must be 'all', a list, or a range.")

    # Set color scheme for slices
    num_selected_slices = len(selected_slices)

    slice_colors = cm.winter(np.linspace(0, 1, num_selected_slices))  # Gradual colors for larger slices

    if plot_type=='surf':
        fig,ax = surf_plot(data,x,y,slice_len,selected_slices)
    elif plot_type=='superimposed':
        fig,ax = superimposed_plot(data,x,y,selected_slices,slice_colors)
    elif plot_type=='stacked':
        fig,ax = stack_plot(data,x,y,selected_slices,slice_colors,spacing)
    elif plot_type=='pcolor':
        fig,ax = pcolor_plot(data,x,y,slice_len,selected_slices)
    
    return fig,ax

def stack_plot(data,x,y,selected_slices,slice_colors,spacing):

    fig,ax = plt.subplots()
    for idx, slice_idx in enumerate(selected_slices):
        slice_data = np.real(data[slice_idx]) if np.iscomplexobj(data) else data[slice_idx]
        ax.plot(x,slice_data + idx * spacing, color=slice_colors[idx % len(slice_colors)], alpha=0.7)

    return fig,ax

def surf_plot(data,x,y,slice_len,selected_slices):
    fig,ax = plt.subplots(subplot_kw={"projection": "3d"})
    X, Y = np.meshgrid(x[range(slice_len)], y[selected_slices])
    Z = np.real(data[selected_slices, :]) if np.iscomplexobj(data) else data[selected_slices, :]
    surf = ax.plot_surface(X, Y, Z, cmap='viridis')
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)

    return fig,ax

def superimposed_plot(data,x,y,selected_slices,slice_colors):
    fig,ax = plt.subplots()
    for idx, slice_idx in enumerate(selected_slices):
        slice_data = np.real(data[slice_idx]) if np.iscomplexobj(data) else data[slice_idx]
        ax.plot(x,slice_data, color=slice_colors[idx % len(slice_colors)], alpha=0.5, label=f'Slice {slice_idx}' if idx == 0 else "_nolegend_")
    
    return fig,ax


def pcolor_plot(data,x,y,slice_len,selected_slices):
    fig,ax = plt.subplots()
    X, Y = np.meshgrid(x[range(slice_len)], y[selected_slices])
    Z = np.real(data[selected_slices, :]) if np.iscomplexobj(data) else data[selected_slices, :]
    pc = ax.pcolor(X, Y, Z, cmap='jet')
    fig.colorbar(pc)

    return fig,ax

def interactive_points_selector(x,y):
    fig,ax =plt.subplots()
    ax.plot(x,y)
    ax.set_title('Select points by left click. Click Done after selecting all points.')
    selected_points = []

    def clicked(event):
        if event.inaxes == ax:
            x_id = event.xdata
            idx = int((np.abs(x - x_id)).argmin())
            selected_points.append(idx)
            ax.plot(x[idx],y[idx],'rx')
            fig.canvas.draw()
    def done(event):
        plt.close(fig)
    
    done_button_ax = plt.axes([0.8, 0.05, 0.1, 0.075])
    done_button = Button(done_button_ax, 'Done')
    done_button.on_clicked(done)
    fig.canvas.mpl_connect('button_press_event', clicked)

    # block function until figure is closed.
    plt.show(block=True)
    
    ## sort the points
    selected_points_sorted = sorted(selected_points, key=lambda idx: x[idx])

    return np.unique(np.array(selected_points_sorted, dtype=int))
