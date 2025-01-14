import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.widgets import Button
import warnings
warnings.simplefilter('always')

color_cycle = plt.cm.tab10.colors[:10]

def eprplot(eprdata_list, plot_type='stacked', slices='all', spacing=0.5,plot_imag=True,g_scale=False):

    """
    Plot one or multiple EPR data objects for visualization and comparison.

    Parameters
    ----------
    eprdata_list : list of EprData
        A list of `EprData` objects to be plotted. Each object should have the following attributes:
        - `filepath` (str): Path to the data file.
        - `data` (ndarray): Data array, which can be 1D or 2D, real or complex.
        - `acq_param` (dict): Acquisition parameters.
    
    plot_type : {'stacked', 'superimposed', 'surf', 'contour'}, optional
        The type of plot to generate for 2D data. Options are:
        - 'stacked' (default): Stacks slices with specified spacing.
        - 'superimposed': Overlays all slices.
        - 'surf': Creates a 3D surface plot.
        - 'contour': Creates a 2D contour plot.

    slices : {'all', list, range}, optional
        Specifies which slices to plot for 2D data. Options include:
        - 'all' (default): Plots all slices.
        - A list of integers: Specifies the indices of slices to plot.
        - A range object: Specifies a range of slice indices.

    spacing : float, optional
        Spacing between slices for 'stacked' or 'superimposed' plots. Default is 0.5.

    plot_imag : bool, optional
        If `True`, includes the imaginary part of the data in the plot. Default is `True`.

    g_scale : bool, optional
        If `True` and `EprData.g` is not `None`, plots the data on a g-factor scale 
        and inverts the x-axis. Default is `False`.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the plot.
    ax : matplotlib.axes._axes.Axes
        The axes object of the plot.

    Notes
    -----
    - For 1D data, all `EprData` objects in the list must have 1D data.
    - For 2D data, all `EprData` objects in the list must have 2D data.
    - The function automatically handles plotting based on the data dimensions 
      (1D or 2D) and the specified plot type.
    - If `g_scale` is enabled and `EprData.g` is available, the x-axis is inverted 
      for better visualization of g-factor values.
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

    fig.set_size_inches((4,3))
    fig.tight_layout()
    if g_scale and eprdata_list[0].g is not None: 
        ax.invert_xaxis()
    
    plt.show()

    return fig,ax


def plot_1d(eprdata_list,g_scale,plot_imag=True):

    """
    Plot 1D EPR data from multiple `EprData` objects.

    Parameters
    ----------
    eprdata_list : list of EprData
        A list of `EprData` objects to be plotted. Each object should have the following attributes:
        - `data` (ndarray): 1D data array (real or complex).
        - `x` (ndarray): x-axis values corresponding to the data.
        - `g` (ndarray, optional): g-factor values, if applicable.
    
    g_scale : bool
        If `True`, plots the data on a g-factor scale (using `g` if available). Default is `False`.

    plot_imag : bool, optional
        If `True`, includes the imaginary part of the data in the plot for complex data. Default is `True`.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the plot.
    ax : matplotlib.axes._axes.Axes
        The axes object of the plot.

    Notes
    -----
    - If `g_scale` is enabled and the `g` attribute is present in the `EprData` object, 
      it will be used for the x-axis. Otherwise, the x-values (`x`) will be used.
    - Complex data is plotted with the real and imaginary parts (if `plot_imag` is `True`).
    - The function uses a cycling color scheme for each plot in `eprdata_list`.
    """
    
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

    """
    Plot 2D EPR data from multiple `EprData` objects.

    Parameters
    ----------
    eprdata_list : list of EprData
        A list of `EprData` objects to be plotted. Each object should have the following attributes:
        - `data` (ndarray): 2D data array.
        - `x` (ndarray): x-axis values corresponding to the data.
        - `y` (ndarray): y-axis values corresponding to the data.
        - `g` (ndarray, optional): g-factor values, if applicable.
    
    g_scale : bool
        If `True`, plots the data on a g-factor scale (using `g` if available). Default is `False`.

    plot_type : {'stacked', 'superimposed', 'surf', 'pcolor'}, optional
        The type of plot to generate for the 2D data. Options are:
        - 'stacked' (default): Stacks slices with specified spacing.
        - 'superimposed': Overlays slices on the same plot.
        - 'surf': Creates a 3D surface plot.
        - 'pcolor': Creates a pseudocolor plot.

    slices : {'all', list, range}, optional
        Specifies which slices to plot for the 2D data. Options include:
        - 'all' (default): Plots all slices.
        - A list of integers: Specifies the indices of slices to plot.
        - A range object: Specifies a range of slice indices.

    spacing : float, optional
        Spacing between slices for 'stacked' and 'superimposed' plots. Default is 0.5.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the plot.
    ax : matplotlib.axes._axes.Axes
        The axes object of the plot.

    Notes
    -----
    - For 2D data, the function selects slices based on the `slices` parameter and 
      visualizes them using one of the specified plot types.
    - The color scheme for the slices is determined by a gradual color map.
    - If `g_scale` is enabled and the `g` attribute is available in the `EprData` object, 
      it will be used for the x-axis. Otherwise, the x-values (`x`) will be used.
    """

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

    """
    Create a stacked plot for 2D EPR data slices.

    Parameters
    ----------
    data : ndarray
        The 2D data array from which the slices will be plotted.
    x : ndarray
        The x-axis values corresponding to the data.
    y : ndarray
        The y-axis values corresponding to the data.
    selected_slices : list of int
        A list of slice indices to be plotted.
    slice_colors : ndarray
        An array of colors to be used for each slice.
    spacing : float
        The vertical spacing between stacked slices.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the stacked plot.
    ax : matplotlib.axes._axes.Axes
        The axes object of the plot.

    Notes
    -----
    - This function plots each slice of the 2D data array, offset vertically by the 
      specified `spacing` to create a stacked appearance.
    - The slices are drawn with colors from the `slice_colors` array, and the transparency 
      is controlled by the `alpha` parameter.
    - Complex data is plotted using the real part only.
    """

    fig,ax = plt.subplots()
    for idx, slice_idx in enumerate(selected_slices):
        slice_data = np.real(data[slice_idx]) if np.iscomplexobj(data) else data[slice_idx]
        ax.plot(x,slice_data + idx * spacing, color=slice_colors[idx % len(slice_colors)], alpha=0.7)

    return fig,ax

def surf_plot(data,x,y,slice_len,selected_slices):

    """
    Create a 3D surface plot for selected slices of 2D EPR data.

    Parameters
    ----------
    data : ndarray
        The 2D data array from which the slices will be plotted.
    x : ndarray
        The x-axis values corresponding to the data.
    y : ndarray
        The y-axis values corresponding to the data.
    slice_len : int
        The length of each slice along the x-axis.
    selected_slices : list of int
        A list of slice indices to be plotted.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the surface plot.
    ax : matplotlib.axes._axes.Axes
        The axes object of the plot.

    Notes
    -----
    - This function creates a 3D surface plot with `x` and `y` as the axes, and the 
      corresponding data values (`Z`) from the selected slices.
    - Complex data is plotted using the real part only.
    - A color bar is added to the plot to indicate the scale of the surface values.
    """

    fig,ax = plt.subplots(subplot_kw={"projection": "3d"})
    X, Y = np.meshgrid(x[range(slice_len)], y[selected_slices])
    Z = np.real(data[selected_slices, :]) if np.iscomplexobj(data) else data[selected_slices, :]
    surf = ax.plot_surface(X, Y, Z, cmap='viridis')
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)

    return fig,ax

def superimposed_plot(data,x,y,selected_slices,slice_colors):

    """
    Create a superimposed plot for selected slices of 2D EPR data.

    Parameters
    ----------
    data : ndarray
        The 2D data array from which the slices will be plotted.
    x : ndarray
        The x-axis values corresponding to the data.
    y : ndarray
        The y-axis values corresponding to the data.
    selected_slices : list of int
        A list of slice indices to be plotted.
    slice_colors : ndarray
        An array of colors to be used for each slice.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the superimposed plot.
    ax : matplotlib.axes._axes.Axes
        The axes object of the plot.

    Notes
    -----
    - This function overlays all selected slices onto a single plot.
    - Complex data is plotted using the real part only.
    - Each slice is plotted with a different color from the `slice_colors` array, 
      and transparency is controlled by the `alpha` parameter.
    - Only the first slice is labeled in the legend, others are excluded using "_nolegend_".
    """

    fig,ax = plt.subplots()
    for idx, slice_idx in enumerate(selected_slices):
        slice_data = np.real(data[slice_idx]) if np.iscomplexobj(data) else data[slice_idx]
        ax.plot(x,slice_data, color=slice_colors[idx % len(slice_colors)], alpha=0.5, label=f'Slice {slice_idx}' if idx == 0 else "_nolegend_")
    
    return fig,ax


def pcolor_plot(data,x,y,slice_len,selected_slices):

    """
    Create a pseudocolor plot for selected slices of 2D EPR data.

    Parameters
    ----------
    data : ndarray
        The 2D data array from which the slices will be plotted.
    x : ndarray
        The x-axis values corresponding to the data.
    y : ndarray
        The y-axis values corresponding to the data.
    slice_len : int
        The length of each slice along the x-axis.
    selected_slices : list of int
        A list of slice indices to be plotted.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the pseudocolor plot.
    ax : matplotlib.axes._axes.Axes
        The axes object of the plot.

    Notes
    -----
    - This function creates a pseudocolor plot (a 2D heatmap) for the selected slices of the data.
    - Complex data is plotted using the real part only.
    - A color bar is added to the plot to indicate the scale of the values.
    """

    fig,ax = plt.subplots()
    X, Y = np.meshgrid(x[range(slice_len)], y[selected_slices])
    Z = np.real(data[selected_slices, :]) if np.iscomplexobj(data) else data[selected_slices, :]
    pc = ax.pcolor(X, Y, Z, cmap='jet')
    fig.colorbar(pc)

    return fig,ax

def interactive_points_selector(x,y):

    """
    Interactively select points from a plot of 1D EPR data.

    Parameters
    ----------
    x : ndarray
        The x-axis values corresponding to the data.
    y : ndarray
        The y-axis values corresponding to the data.

    Returns
    -------
    selected_points : ndarray
        An array of the indices of the selected points, sorted in ascending order.

    Notes
    -----
    - This function creates an interactive plot where points can be selected by left-clicking 
      on the plot. After selecting all desired points, the user can click the 'Done' button 
      to finalize the selection.
    - The function returns the indices of the selected points, sorted in the order of their 
      x-axis values.
    """
    
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
