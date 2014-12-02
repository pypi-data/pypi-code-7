'''
Convenience functions for dealing with Matplotlib colormaps

Created on Nov 30, 2014

@author: gdelraye
'''

#--- Import libraries:
import colorobject

#--- Parse color maps:
def cmap2colorlist(cmap):
    '''Convert a Matplotlib colormap into a colorlist object
    
    Examples::
    
        >>> from matplotlib import pyplot
        >>> from matplotlib.colors import LinearSegmentedColormap
        >>> cmap = pyplot.get_cmap('winter')
        >>> print cmap2colorlist(cmap)
        [[0.0, 0.0, 1.0, 1.0], [0.0, 1.0, 0.5, 1.0]]
        >>> cdict = {'red'  :  ((0., 0., 0.), (0.5, 0.25, 0.25), (1., 1., 1.)),
        ...          'green':  ((0., 1., 1.), (0.7, 0.0, 0.5), (1., 1., 1.)),
        ...          'blue' :  ((0., 1., 1.), (0.5, 0.0, 0.0), (1., 1., 1.))}
        >>> cmap = LinearSegmentedColormap('discontinuous_cmap', cdict) # Discontinuous colormap
        >>> print cmap2colorlist(cmap)
        [[0.0, 1.0, 1.0, 1.0], [0.25, 0.0, 0.0, 1.0], [0.25, 0.5, 0.0, 1.0], [1.0, 1.0, 1.0, 1.0]]
    '''
    blu1, blu2 = zip(*cmap._segmentdata['blue'])[1:]
    red1, red2 = zip(*cmap._segmentdata['red'])[1:]
    grn1, grn2 = zip(*cmap._segmentdata['green'])[1:]
    red, green, blue = [], [], []
    for (r1, r2), (g1, g2), (b1, b2) in zip(zip(red1, red2), zip(grn1, grn2), 
                                            zip(blu1, blu2)):
        # This is necessary in case of discontinuous colormaps:
        if r1 == r2 and g1 == g2 and b1 == b2:
            red.append(r1)
            green.append(g1)
            blue.append(b1)
        else:
            red.extend((r1, r2))
            green.extend((g1, g2))
            blue.extend((b1, b2))
    return colorobject.rgba2colorlist(zip(red, green, blue))

def cmap_positions(cmap):
    '''Get color positions from a Matplotlib colormap
    
    Examples::
    
        >>> from matplotlib import pyplot
        >>> cmap = pyplot.get_cmap('winter')
        >>> print cmap_positions(cmap)
        (0.0, 1.0)
    '''
    return zip(*cmap._segmentdata['red'])[0]

#--- Modify color maps:
def cmap_adjust(cmap, methodname, *args, **kwargs):
    '''Change a matplotlib colormap using one of the colorobjects methods
    
    Examples::
    
        >>> from matplotlib import pyplot
        >>> cmap = pyplot.get_cmap('summer')
        >>> adjusted = cmap_adjust(cmap, 'dynamic_range', 0.25, 0.6)
        >>> print adjusted.name
        summer_adjusted
        >>> print cmap._segmentdata['blue']
        ((0.0, 0.4, 0.4), (1.0, 0.4, 0.4))
        >>> print [colorobject.round_rgba(entry, 1) for entry in adjusted._segmentdata['blue']]
        [[0.0, 0.4, 0.4], [1.0, 0.2, 0.2]]
    '''
    positions = cmap_positions(cmap)
    name = '{0}_adjusted'.format(cmap.name)
    clist = cmap2colorlist(cmap)
    clist = getattr(clist, methodname)(*args, **kwargs)
    return clist.LinearSegmentedColormap(positions, name)

def cmap_darken(cmap):
    '''Modify color map to be visible against a white background'''
    return cmap_adjust(cmap, 'dynamic_range', 0.0, 0.7)
    
def cmap_lighten(cmap):
    '''Modify color map to be visible against a black background'''
    return cmap_adjust(cmap, 'dynamic_range', 0.3, 1.0)
    
    #--- Test:
if __name__ == '__main__':
    # Do the doctests
    import doctest
    doctest.testmod() 
    
    
    
