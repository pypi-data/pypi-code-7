#TEST FOR ZONAL MEAN PLOTTER
from filehandler import FileHandler
#from plotter import Plotter
import matplotlib
#mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

fn = '/home/illing/workspace/murcss2/integration/metrics/1_1_ta_baseline1_output_mpi-esm-lr_decs4e_1980-2000_correlation.nc'

def plotZM(data, x, y, plotOpt=None, modelLevels=None, surfacePressure=None):
    """Create a zonal mean contour plot of one variable
    plotOpt is a dictionary with plotting options:
      'scale_factor': multiply values with this factor before plotting
      'units': a units label for the colorbar
      'levels': use list of values as contour intervals
      'title': a title for the plot
    modelLevels: a list of pressure values indicating the model vertical resolution. If present,
        a small side panel will be drawn with lines for each model level
    surfacePressure: a list (dimension len(x)) of surface pressure values. If present, these will
        be used to mask out regions below the surface
    """
    # explanation of axes:
    #   ax1: primary coordinate system latitude vs. pressure (left ticks on y axis)
    #   ax2: twinned axes for altitude coordinates on right y axis
    #   axm: small side panel with shared y axis from ax2 for display of model levels
    # right y ticks and y label will be drawn on axr if modelLevels are given, else on ax2
    #   axr: pointer to "right axis", either ax2 or axm

    if plotOpt is None: plotOpt = {}
    labelFontSize = "small"
    # create figure and axes
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    # scale data if requested
    scale_factor = plotOpt.get('scale_factor', 1.0)
    #pdata = data * scale_factor
    # determine contour levels to be used; default: linear spacing, 20 levels
    clevs = plotOpt.get('levels', np.linspace(data.min(), data.max(), 20))
    # map contour values to colors
    def divi(x):
        return float(x)/10
        
    colorSteps = map(divi,range(int(-1*10),int((1*10)+1),1))#(vmax-vmin)/2))
    print colorSteps
    my_cmap = plt.cm.RdBu_r
    #my_cmap.set_bad("grey")                         #set missing value color
    maskedArray = np.ma.masked_outside(data, -0.8e20, 0.8e20)
    #discrete colormap
    norm = matplotlib.colors.BoundaryNorm(colorSteps, my_cmap.N)
    norm = matplotlib.colors.BoundaryNorm(colorSteps, my_cmap.N)
    # draw the (filled) contours
    #contour = ax1.contourf(x, y, maskedArray,norm=norm, cmap=my_cmap, levels=colorSteps, interpolation='none')
    #contour = ax1.pcolormesh(x, y, maskedArray, cmap=my_cmap, norm=norm)
    contour = plt.imshow(maskedArray, cmap=my_cmap, norm=norm,interpolation='none')
    # mask out surface pressure if given
#    if not surfacePressure is None: 
#        ax1.fill_between(x, surfacePressure, surfacePressure.max(), color="white")    
    # add a title
    title = plotOpt.get('title', 'Vertical cross section')
    ax1.set_title(title)
    # add colorbar
    # Note: use of the ticks keyword forces colorbar to draw all labels
#    fmt = matplotlib.ticker.FormatStrFormatter("%g")
    cbar = fig.colorbar(contour, ax=ax1, orientation='horizontal',ticks=colorSteps,)
    #cbar.set_label(plotOpt.get('units', ''))
    for t in cbar.ax.get_xticklabels():
        t.set_fontsize(labelFontSize)
    # set up y axes: log pressure labels on the left y axis, altitude labels
    # according to model levels on the right y axis
#    ax1.set_ylabel("Pressure [Pa]")
#    #ax1.set_yscale('log')
#    ax1.set_ylim(10.*np.ceil(y.max()/10.), y.min()) # avoid truncation of 1000 hPa
#    subs = [1,2,5]
#    if y.max()/y.min() < 30.:
#        subs = [1,2,3,4,5,6,7,8,9]
#    y1loc = matplotlib.ticker.LogLocator(base=10., subs=subs)
#    ax1.yaxis.set_major_locator(y1loc)
#    fmt = matplotlib.ticker.FormatStrFormatter("%g")
#    ax1.yaxis.set_major_formatter(fmt)
#    for t in ax1.get_yticklabels():
#        t.set_fontsize(labelFontSize)
#    # change values and font size of x labels
#    ax1.set_xlabel('Latitude [degrees]')
#    xloc = matplotlib.ticker.FixedLocator(np.arange(-90.,91.,30.))
#    ax1.xaxis.set_major_locator(xloc)
    for t in ax1.get_xticklabels():
        t.set_fontsize(labelFontSize)
    # draw horizontal lines to the right to indicate model levels

    # show plot
    plt.xticks(range(0,len(x)),x)
    plt.yticks(range(0,len(y)),y)
    plt.show()

def plotZM2(data,lat,plev):
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    colorSteps = [-1,-0.8,-0.6,-0.4,-0.2,0.0,0.2,0.4,0.6,0.8,1.0]
    colorSteps = np.linspace(-1,1,21)
    colorTicks = colorSteps[0::2]
    my_cmap = plt.cm.RdBu_r
    my_cmap.set_bad("grey")                         #set missing value color
    maskedArray = np.ma.masked_outside(data, -0.8e20, 0.8e20)
    #discrete colormap
    norm = matplotlib.colors.BoundaryNorm(colorSteps, my_cmap.N)
    cs = ax1.imshow(maskedArray, interpolation="nearest", cmap=my_cmap, norm=norm)
    cbar = fig.colorbar(cs, ax=ax1, orientation='vertical',ticks=colorSteps[0::2])
    ax1.set_xlabel('Latitude [degrees]')
    ax1.set_ylabel("Pressure [Pa]")
    plt.xticks(range(1,len(lat),3),lat[1::3])
    plt.yticks(range(0,len(plev),1),plev[0::1])
    
    

value = FileHandler.openNetCDFFile(fn, 'plev')
print value

plotZM2(value['variable'], value['lat'], value['plev'])
plotZM2(np.flipud(value['variable']), value['lat'], np.flipud(value['plev']))

from plotter import Plotter
Plotter.plotVerticalProfile(fn,-1,1)

plt.show()
#plotZM(value['variable'], value['lat'], value['plev'])





#TEST FROM LEADTIMES PLOTTER
#result_list = [['/scratch/b324057/evaluation_system/output/murcss/20141106-135133_tas_baseline1_output_mpi-m_mpi-esm-lr_decs4e_baseline0_output1_mpi-m_mpi-esm-lr_decadal_hadcrut3v_1960-2000/1-1/baseline1_output_mpi-esm-lr_decs4e_input1/accuracy/1_1_tas_baseline1_output_mpi-esm-lr_decs4e_1960-2000_correlation.nc_masked', '/scratch/b324057/evaluation_system/output/murcss/20141106-135133_tas_baseline1_output_mpi-m_mpi-esm-lr_decs4e_baseline0_output1_mpi-m_mpi-esm-lr_decadal_hadcrut3v_1960-2000/1-1/baseline1_output_mpi-esm-lr_decs4e_input1/accuracy/1_1_tas_baseline1_output_mpi-esm-lr_decs4e_1960-2000_conditional_bias.nc_masked', '/scratch/b324057/evaluation_system/output/murcss/20141106-135133_tas_baseline1_output_mpi-m_mpi-esm-lr_decs4e_baseline0_output1_mpi-m_mpi-esm-lr_decadal_hadcrut3v_1960-2000/1-1/baseline1_output_mpi-esm-lr_decs4e_input1/accuracy/1_1_tas_baseline1_output_mpi-esm-lr_decs4e_1960-2000_msss.nc_masked', '/scratch/b324057/evaluation_system/output/murcss/20141106-135133_tas_baseline1_output_mpi-m_mpi-esm-lr_decs4e_baseline0_output1_mpi-m_mpi-esm-lr_decadal_hadcrut3v_1960-2000/1-1/baseline0_output1_mpi-esm-lr_decadal_input2/accuracy/1_1_tas_baseline0_output1_mpi-esm-lr_decadal_1960-2000_correlation.nc_masked', '/scratch/b324057/evaluation_system/output/murcss/20141106-135133_tas_baseline1_output_mpi-m_mpi-esm-lr_decs4e_baseline0_output1_mpi-m_mpi-esm-lr_decadal_hadcrut3v_1960-2000/1-1/baseline0_output1_mpi-esm-lr_decadal_input2/accuracy/1_1_tas_baseline0_output1_mpi-esm-lr_decadal_1960-2000_conditional_bias.nc_masked', '/scratch/b324057/evaluation_system/output/murcss/20141106-135133_tas_baseline1_output_mpi-m_mpi-esm-lr_decs4e_baseline0_output1_mpi-m_mpi-esm-lr_decadal_hadcrut3v_1960-2000/1-1/baseline0_output1_mpi-esm-lr_decadal_input2/accuracy/1_1_tas_baseline0_output1_mpi-esm-lr_decadal_1960-2000_msss.nc_masked', '/scratch/b324057/evaluation_system/output/murcss/20141106-135133_tas_baseline1_output_mpi-m_mpi-esm-lr_decs4e_baseline0_output1_mpi-m_mpi-esm-lr_decadal_hadcrut3v_1960-2000/1-1/baseline1_output_mpi-esm-lr_decs4e_input1_vs_baseline0_output1_mpi-esm-lr_decadal_input2/accuracy/1_1_tas_baseline1_output_mpi-esm-lr_decs4e_vs_baseline0_output1_mpi-esm-lr_decadal_1960-2000_correlation.nc_masked', '/scratch/b324057/evaluation_system/output/murcss/20141106-135133_tas_baseline1_output_mpi-m_mpi-esm-lr_decs4e_baseline0_output1_mpi-m_mpi-esm-lr_decadal_hadcrut3v_1960-2000/1-1/baseline1_output_mpi-esm-lr_decs4e_input1_vs_baseline0_output1_mpi-esm-lr_decadal_input2/accuracy/1_1_tas_baseline1_output_mpi-esm-lr_decs4e_vs_baseline0_output1_mpi-esm-lr_decadal_1960-2000_conditional_bias.nc_masked', '/scratch/b324057/evaluation_system/output/murcss/20141106-135133_tas_baseline1_output_mpi-m_mpi-esm-lr_decs4e_baseline0_output1_mpi-m_mpi-esm-lr_decadal_hadcrut3v_1960-2000/1-1/baseline1_output_mpi-esm-lr_decs4e_input1_vs_baseline0_output1_mpi-esm-lr_decadal_input2/accuracy/1_1_tas_baseline1_output_mpi-esm-lr_decs4e_vs_baseline0_output1_mpi-esm-lr_decadal_1960-2000_msss.nc_masked'], ['/scratch/b324057/evaluation_system/output/murcss/20141106-135133_tas_baseline1_output_mpi-m_mpi-esm-lr_decs4e_baseline0_output1_mpi-m_mpi-esm-lr_decadal_hadcrut3v_1960-2000/2-2/baseline1_output_mpi-esm-lr_decs4e_input1/accuracy/2_2_tas_baseline1_output_mpi-esm-lr_decs4e_1960-2000_correlation.nc_masked', '/scratch/b324057/evaluation_system/output/murcss/20141106-135133_tas_baseline1_output_mpi-m_mpi-esm-lr_decs4e_baseline0_output1_mpi-m_mpi-esm-lr_decadal_hadcrut3v_1960-2000/2-2/baseline1_output_mpi-esm-lr_decs4e_input1/accuracy/2_2_tas_baseline1_output_mpi-esm-lr_decs4e_1960-2000_conditional_bias.nc_masked', '/scratch/b324057/evaluation_system/output/murcss/20141106-135133_tas_baseline1_output_mpi-m_mpi-esm-lr_decs4e_baseline0_output1_mpi-m_mpi-esm-lr_decadal_hadcrut3v_1960-2000/2-2/baseline1_output_mpi-esm-lr_decs4e_input1/accuracy/2_2_tas_baseline1_output_mpi-esm-lr_decs4e_1960-2000_msss.nc_masked', '/scratch/b324057/evaluation_system/output/murcss/20141106-135133_tas_baseline1_output_mpi-m_mpi-esm-lr_decs4e_baseline0_output1_mpi-m_mpi-esm-lr_decadal_hadcrut3v_1960-2000/2-2/baseline0_output1_mpi-esm-lr_decadal_input2/accuracy/2_2_tas_baseline0_output1_mpi-esm-lr_decadal_1960-2000_correlation.nc_masked', '/scratch/b324057/evaluation_system/output/murcss/20141106-135133_tas_baseline1_output_mpi-m_mpi-esm-lr_decs4e_baseline0_output1_mpi-m_mpi-esm-lr_decadal_hadcrut3v_1960-2000/2-2/baseline0_output1_mpi-esm-lr_decadal_input2/accuracy/2_2_tas_baseline0_output1_mpi-esm-lr_decadal_1960-2000_conditional_bias.nc_masked', '/scratch/b324057/evaluation_system/output/murcss/20141106-135133_tas_baseline1_output_mpi-m_mpi-esm-lr_decs4e_baseline0_output1_mpi-m_mpi-esm-lr_decadal_hadcrut3v_1960-2000/2-2/baseline0_output1_mpi-esm-lr_decadal_input2/accuracy/2_2_tas_baseline0_output1_mpi-esm-lr_decadal_1960-2000_msss.nc_masked', '/scratch/b324057/evaluation_system/output/murcss/20141106-135133_tas_baseline1_output_mpi-m_mpi-esm-lr_decs4e_baseline0_output1_mpi-m_mpi-esm-lr_decadal_hadcrut3v_1960-2000/2-2/baseline1_output_mpi-esm-lr_decs4e_input1_vs_baseline0_output1_mpi-esm-lr_decadal_input2/accuracy/2_2_tas_baseline1_output_mpi-esm-lr_decs4e_vs_baseline0_output1_mpi-esm-lr_decadal_1960-2000_correlation.nc_masked', '/scratch/b324057/evaluation_system/output/murcss/20141106-135133_tas_baseline1_output_mpi-m_mpi-esm-lr_decs4e_baseline0_output1_mpi-m_mpi-esm-lr_decadal_hadcrut3v_1960-2000/2-2/baseline1_output_mpi-esm-lr_decs4e_input1_vs_baseline0_output1_mpi-esm-lr_decadal_input2/accuracy/2_2_tas_baseline1_output_mpi-esm-lr_decs4e_vs_baseline0_output1_mpi-esm-lr_decadal_1960-2000_conditional_bias.nc_masked', '/scratch/b324057/evaluation_system/output/murcss/20141106-135133_tas_baseline1_output_mpi-m_mpi-esm-lr_decs4e_baseline0_output1_mpi-m_mpi-esm-lr_decadal_hadcrut3v_1960-2000/2-2/baseline1_output_mpi-esm-lr_decs4e_input1_vs_baseline0_output1_mpi-esm-lr_decadal_input2/accuracy/2_2_tas_baseline1_output_mpi-esm-lr_decs4e_vs_baseline0_output1_mpi-esm-lr_decadal_1960-2000_msss.nc_masked']]
#
#input1 = 'baseline1_output_mpi-esm-lr_decs4e_1960-2000_'
#
#to_search = ['correlation','msss']
#
#def getFn(s):
#    return s.split('/')[-1]
#
#def get_files_in_folder(folder):
#    import os
#    import os.path
#    result = list()
#    for dirpath, dirnames, filenames in os.walk(folder):
#        for filename in filenames:
#            result.append(os.path.join(dirpath, filename))
#    return result
#
#result_list = get_files_in_folder('/home/illing/workspace/murcss2/testdata/20141106-135133_tas_baseline1_output_mpi-m_mpi-esm-lr_decs4e_baseline0_output1_mpi-m_mpi-esm-lr_decadal_hadcrut3v_1960-2000/1-1/')
#result_list2 = get_files_in_folder('/home/illing/workspace/murcss2/testdata/20141106-135133_tas_baseline1_output_mpi-m_mpi-esm-lr_decs4e_baseline0_output1_mpi-m_mpi-esm-lr_decadal_hadcrut3v_1960-2000/2-2/')
#result_list = [result_list,result_list2]
#
#result_list = list()
#
#flag_list = ['baseline1_output_mpi-esm-lr_decs4e_1960-2000',
#         'baseline0_output1_mpi-esm-lr_decadal_1960-2000',
#         'baseline1_output_mpi-esm-lr_decs4e_vs_baseline0_output1_mpi-esm-lr_decadal_1960-2000']
#plot_list = [('correlation','Anomaly Correlation',[-1,1]),('msss','Mean Squared Error Skill Score',[-2,1])]
#
#for i in range(1,11):
#    result_list.append(get_files_in_folder('/home/illing/workspace/murcss2/testdata/20141106-151736_tas_baseline1_output_mpi-m_mpi-esm-lr_decs4e_baseline0_output1_mpi-m_mpi-esm-lr_decadal_hadcrut3v_1960-2000/'+str(i)+'-'+str(i)))
#
#correlation = list()
#msss = list()
#
#from plotter import Plotter
#
#Plotter.plotLeadtimeseries(result_list,flag_list,plot_list)