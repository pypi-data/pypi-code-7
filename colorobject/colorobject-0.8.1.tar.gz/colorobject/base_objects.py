'''
Handle color type conversions, transformations, and colormap construction through a 
color and colorlist object. Intended to be compatible with Matplotlib.

Created on Nov 28, 2014

@author: gdelraye
'''

#--- Import packages:
# Python standard library
import colorsys # core color conversion library
# 3rd party libraries
import matplotlib.colors # additional color conversions

#--- Global operations:
matplotlib_colordict = matplotlib.colors.cnames.copy() # Save html color to hex dictionary
matplotlib_colordict.update((key, matplotlib.colors.hex2color(value)
                             ) for key, value in matplotlib_colordict.items()) # Convert hex to rgb
matplotlib_colordict.update(matplotlib.colors.ColorConverter.colors) # Add single letter colors (e.g. 'r')
matplotlib_namedict = {v: k for k, v in matplotlib_colordict.items()} # Map RGB tuple to color name

#--- Color objects:
class color(list):
    '''Handle color type conversions and transformations through a color object.
    Because the object is at base an rgb list (is it an extension of the list 
    class), it can be passed directly to any Matplotlib plotting commands. 
    
    Features include: 
        * Get or set the lightness, saturation, or hue of a color object.
        * Interconvert between hls, hsv, rgb floats (where elements range from 0-1)
          rgb integers (where elements range from 0-255), rgb hexadecimal strings,
          and valid Matplotlib color names.
        * Find the closest named Matplotlib color (e.g. 'papayawhip') for a color object.
        * Additive blending of two color objects
    '''
    def __init__(self, color, colortype = 'rgba'):
        '''Create a color object as an rgba tuple
        
        Inputs:
            * color (seq or str) - color descriptor, could be a tuple (e.g. 3-element rgb or hsv)
              or string (e.g. rgb hex or Matplotlib color name). Defaults to rgba (3-element rgb + 
              alpha)
            * colortype (str) - color descriptor type (e.g. 'hex' or 'hsv'). Defaults to 'rgba'.
        
        Examples::
        
            >>> rgba = (0.5, 0.5, 0.5, 1.0)
            >>> print color(rgba) # Specify with rgba tuple
            [0.5, 0.5, 0.5, 1.0]
            >>> hls = (0.0, 0.5, 0.0)
            >>> print color(hls, 'hls') # Specify with hls (hue, lightness, saturation)
            [0.5, 0.5, 0.5, 1.0]
            >>> color(rgba, 'non-existant color type') # Attempt non-existant color type
            Traceback (most recent call last):
            ...
            AttributeError: Unrecognized colortype 'non-existant color type'
        '''
        if colortype in self.__class__.__dict__.keys():
            setattr(self, colortype, color)
        else:
            raise AttributeError, "Unrecognized colortype '{0}'".format(colortype)
        
    
    #--- Color transformations:
    def saturate(self, saturation_factor):
        '''Change the saturation of a rgba tuple by adding
        saturation_factor to the the saturation
        
        Examples::
        
            >>> rgba = (0.5, 0.6, 0.5, 1.0)
            >>> print round_rgba(color(rgba).saturate(1.0), 1)
            [0.0, 0.6, 0.0, 1.0]
            >>> print round_rgba(color(rgba).saturate(-1.0), 1)
            [0.6, 0.6, 0.6, 1.0]
        '''
        (h, s, v), a = self.hsv, self.alpha
        s = min(1.0, s + saturation_factor) # Change saturation
        s = max(0.0, s)
        return color((h, s, v, a), 'hsv') # Return new color object
    
    def lighten(self, lighten_factor):
        '''Lighten or darken the rgba tuple by adding
        lighten_factor to the brightness
        
        Examples::
        
            >>> rgba = (0.5, 0.5, 0.5, 1.0) # grey
            >>> print color(rgba).lighten(0.5) # white
            [1.0, 1.0, 1.0, 1.0]
        '''
        (h, l, s), a = self.hls, self.alpha
        l = min(1.0, l + lighten_factor) # Change lightness
        l = max(0.0, l)
        return color((h, l, s, a), 'hls') # Return new color object
    
    def blend(self, other, blendtype = 'mean'):
        '''Blend two colorobjects by adding (blendtype = 'add') or 
        averaging (blendtype = 'mean') rgb components
        
        Examples::
        
            >>> color1 = color((0, 0, 0)) # Black
            >>> color2 = color((1, 1, 1)) # White
            >>> print color1.blend(color2, blendtype = 'add') # White
            [1.0, 1.0, 1.0, 1.0]
            >>> print color1.blend(color2, blendtype = 'mean') # Grey
            [0.5, 0.5, 0.5, 1.0]
        '''
        choose_converter = {'mean': self._mean, 'add': self._add}
        converter = choose_converter[blendtype]
        return converter(other)
    
    def rotate(self, rotation):
        '''Rotate color hue by rotation degrees where degrees is in the range 0-360
        
        Examples::
        
            >>> red = color((1.0, 0.0, 0.0), colortype = 'rgba')
            >>> print red.rotate(180) # Cyan 
            [0.0, 1.0, 1.0, 1.0]
        '''
        hue_shift = rotation*1./360 # Convert degrees to 0-1 scale
        a = self[-1]
        h, s, v = self.hsv
        h = (h + hue_shift)%1
        return color((h, s, v, a), colortype = 'hsv')
    
    #--- Properties:
    @property
    def red(self):
        '''Get red channel'''
        return self[0]
    
    @red.setter
    def red(self, r):
        '''Set red channel'''
        g, b, a = self[1:]
        self.__init__((r, g, b, a))
        
    @property
    def green(self):
        '''Get green channel'''
        return self[1]
    
    @green.setter
    def green(self, g):
        '''Set green channel'''
        r, b = self[::2]
        self.__init__((r, g, b, self.alpha))
        
    @property
    def blue(self):
        '''Get blue channel'''
        return self[2]
    
    @blue.setter
    def blue(self, b):
        '''Set blue channel'''
        r, g = self[:-2]
        self.__init__((r, g, b, self.alpha))
    
    @property
    def alpha(self):
        '''Get transparency'''
        return self[-1]
    
    @alpha.setter
    def alpha(self, a):
        '''Set transparency'''
        r, g, b = self[:-1]
        self.__init__((r, g, b, a))
        
    @property
    def lightness(self):
        '''Get lightness'''
        return self.hls[1]
    
    @lightness.setter
    def lightness(self, l):
        '''Set lightness'''
        h, s = self.hls[::2]
        self.__init__((h, l, s, self.alpha), colortype = 'hls')
        
    @property
    def saturation(self):
        '''Get saturation'''
        return self.hls[-1]
    
    @saturation.setter
    def saturation(self, s):
        '''Set saturation'''
        h, l = self.hls[:-1]
        self.__init__((h, l, s, self.alpha), colortype = 'hls')
        
    @property
    def hue(self):
        '''Get hue'''
        return self.hls[0]
    
    @hue.setter
    def hue(self, h):
        '''Set hue'''
        l, s = self.hls[1:]
        self.__init__((h, l, s, self.alpha), colortype = 'hls')
    
    @property
    def rgba(self):
        '''Get rgba (red, green, blue, alpha) tuple where r, g, b, a ranges from 0-1
        
        Examples::
        
            >>> rgba = (0.5, 0.5, 0.5)
            >>> print color(rgba).rgba
            [0.5, 0.5, 0.5, 1.0]
        '''
        return self
    
    @rgba.setter
    def rgba(self, values):
        '''Set color using rgba (red, green, blue, alpha) tuple where r, g, b, a ranges from 0-1
        
        Examples::
        
            >>> rgba = (0.5, 0.5, 0.5, 1.0)
            >>> c = color(rgba)
            >>> c.rgba = rgba
            >>> print c
            [0.5, 0.5, 0.5, 1.0]
        '''
        try:
            r, g, b, a = values
        except ValueError:
            r, g, b = values
            a = 1.0
        list.__init__(self, (r, g, b, a))
    
    @property
    def rgbint(self):
        '''Get rgb (red, green, blue) tuple where r, g, b ranges from 0-255
        
        Examples::
        
            >>> rgba = (0.5, 0.5, 0.5, 1.0)
            >>> print color(rgba).rgbint
            (127, 127, 127)
        '''
        r, g, b = self[:-1]
        return tuple([int(i*255) for i in (r, g, b)])
    
    @rgbint.setter
    def rgbint(self, values):
        '''Set color using rgba (red, green, blue, alpha) tuple where r, g, b ranges from 0-255
        
        Examples::
        
            >>> rgbint = (127, 127, 127) 
            >>> print round_rgba(color(rgbint, 'rgbint'), 1)
            0.5, 0.5, 0.5, 1.0
        '''
        try:
            r, g, b, a = values
        except ValueError:
            r, g, b = values
            a = 1.0
        self.rgba = tuple([i/255. for i in (r, g, b, a*255)])
    
    @property
    def hls(self):
        '''Get hls (hue, lightness, saturation) tuple
        
        Examples::
        
            >>> rgba = (0.5, 0.5, 0.5, 1.0)
            >>> print color(rgba).hls
            (0.0, 0.5, 0.0)
        '''
        r, g, b = self[:-1]
        return colorsys.rgb_to_hls(r, g, b)
    
    @hls.setter
    def hls(self, values):
        '''Set color using hls (hue, lightness, saturation) tuple
        
        Examples::
        
            >>> hls = (0.0, 0.5, 0.0)
            >>> c = color(hls, 'hls')
            >>> print c
            (0.5, 0.5, 0.5, 1.0)
        '''
        try:
            h, l, s, a = values
        except ValueError:
            h, l, s = values
            a = 1.0
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        self.rgba = (r, g, b, a)
        
    @property
    def hsv(self):
        '''Get hsv (hue, saturation, value) tuple
        
        Examples::
        
            >>> rgba = (0.5, 0.5, 0.5, 1.0)
            >>> print color(rgba).hsv
            [ 0.   0.   0.5]
        '''
        r, g, b = self[:-1]
        return matplotlib.colors.rgb_to_hsv((r, g, b))
    
    @hsv.setter
    def hsv(self, values):
        '''Set color using hsv (hue, saturation, value) tuple
        
        Examples::
        
            >>> hsv = (0.0, 0.0, 0.5)
            >>> print color(hsv, 'hsv')
            (0.5, 0.5, 0.5, 1.0)
        '''
        try:
            h, s, v, a = values
        except ValueError:
            h, s, v = values
            a = 1.0
        r, g, b = matplotlib.colors.hsv_to_rgb((h, s, v))
        self.rgba = (r, g, b, a)
    
    @property
    def hex(self):
        '''Get rgb hex string
        
        Examples::
        
            >>> rgba = (0.5, 0.5, 0.5, 1.0)
            >>> print color(rgba).hex
            #808080
        '''
        return matplotlib.colors.rgb2hex(self[:-1])
    
    @hex.setter
    def hex(self, hexstr):
        '''Set color using rgb hex string
        
        Examples::
        
            >>> hex = '#808080'
            >>> print round_rgba(color(hex, 'hex'), 1)
            [0.5, 0.5, 0.5, 1.0]
        '''
        r, g, b = matplotlib.colors.hex2color(hexstr)
        self.rgba = (r, g, b)

    @property
    def name(self):
        '''Get Matplotlib color name (html or single-letter).
        If matching color is not found, returns ValueError
        
        Examples::
        
            >>> rgba = (0, 0, 0, 1)
            >>> print color(rgba).name # 'black' in Matplotlib is also 'k'
            k
        '''
        return matplotlib_namedict[tuple(self[:-1])]
    
    @name.setter
    def name(self, name):
        '''Set color using Matplotlib color name (html or single-letter)
        
        Examples::
        
            >>> name = 'grey'
            >>> print round_rgba(color(name, 'name'), 1)
            0.5, 0.5, 0.5, 1.0
        '''
        r, g, b = matplotlib_colordict[name.lower()]
        self.rgba = (r, g, b)
    
    @property
    def closest_name(self):
        '''Get closest Matplotlib color name.
        
        Examples::
        
            >>> rgba = (0.5, 0.5, 0.5, 1.0)
            >>> print color(rgba).closest_name
            grey
        '''
        web_rgb = matplotlib_colordict.values()
        rgb_distance = [sum(self - color(webcolor)) for webcolor in web_rgb]
        closest_index = rgb_distance.index(min(rgb_distance))
        closest_rgb = web_rgb[closest_index]
        return matplotlib_namedict[closest_rgb]
    
    #--- Helper methods:
    def _add(self, other):
        '''Same as __add__ but imposes a ceiling of 1
        
        Examples::
        
            >>> c1 = color((0.6, 0.6, 0.6))
            >>> c3 = c1 + c1
            >>> print c3 # Simple sum doesn't limit values
            [1.2, 1.2, 1.2, 1.0]
            >>> c4 = c1._add(c1)
            >>> print c4 # Capped addition
            [1.0, 1.0, 1.0, 1.0]
        '''
        color_sum = (self + other)
        color_sum = [min(component, 1.0) for component in color_sum]
        return color(color_sum, colortype = 'rgba')
    
    def _mean(self, other):
        '''Average rgb values between two color objects'''
        return (self + other)*0.5
        
    #--- Magic methods:
    def __sub__(self, other):
        '''Subtract rgb values scaled by alpha for two color objects'''
        self_rgb = (self*self[-1])[:-1]
        other_rgb = (other*other[-1])[:-1]
        r, g, b = [abs(s - o) for s, o in zip(self_rgb, other_rgb)]
        return color((r, g, b, 1.0), colortype = 'rgba')
    
    def __add__(self, other):
        '''Add rgb values scaled by alpha for two color objects'''
        self_rgb = (self*self[-1])[:-1]
        other_rgb = (other*other[-1])[:-1]
        r, g, b = [s + o for s, o in zip(self_rgb, other_rgb)]
        return color((r, g, b, 1.0), colortype = 'rgba')
    
    def __mul__(self, other):
        '''Multiply r, g, b components by a scalar'''
        r, g, b = [component*other for component in self[:-1]]
        a = self[-1]
        return color((r, g, b, a), colortype = 'rgba')

class colorlist(list):
    '''Handle list of color objects, such as for a color cycle or colormap
    Because the object is at base a list of rgb tuples (is it an extension of the 
    list class), it can be passed directly to any Matplotlib plotting commands 
    (e.g. to pyplot.rc).
    
    Features include: 
        * Create a matplotlib colormap object from a colorlist
        * Set the colorcyle of a matplotlib axis object using a colorlist
        * Set the alpha, lightness, saturation, hue, or dynamic range of the entire 
          colorlist
        * Convert the list to Matplotlib color strings, hsv, hls, rgb hexadecimal strings,
          or integer rgb tuples (value ranges from 0-255).
        * Blend the colors in two colorlists together, or rotate the hue of an
          entire colorlist.
    '''
    def __init__(self, *colors):
        '''Store color objects
        
        Inputs:
            * colors - arbitrary number of color objects
        
        Examples::
        
            >>> clist = colorlist(color('black', 'name'), color('grey', 'name'))
            >>> len(clist)
            2
        '''
        list.__init__(self, colors)
        
    #--- Colorlist conversions:
    def LinearSegmentedColormap(self, positions = None, name = 'custom_cmap'):
        '''Create a linear segmented colormap from the colors in the list
        
        Examples::
        
            >>> clist = colorlist(color('black', 'name'), color('grey', 'name'))
            >>> cmap = clist.LinearSegmentedColormap(name = 'black2grey')
            >>> print cmap.name
            black2grey
            >>> clist = rgba2colorlist([(0, 0, 0), (0, 0, 0.5), (0.5, 0, 0), 
            ...                        (0, 0, 0), (1, 1, 1)])
            >>> positions = (0, 0.33, 0.33, 0.66, 1.0) # Discontinuous colormap
            >>> cmap = clist.LinearSegmentedColormap(positions)
            >>> print cmap._segmentdata['blue']
            [(0, 0, 0), (0.33, 0.5, 0), (0.33, 0, 0), (0.66, 1, 1)]
            >>> print cmap._segmentdata['red']
            [(0, 0, 0), (0.33, 0, 0.5), (0.33, 0, 0), (0.66, 1, 1)]
            
        '''
        if positions is None: # Default to evenly-spaced positions from 0-1
            n_positions = len(self)
            positions = colorlist._default_positions(n_positions)
        unique = list(set(positions))
        unique.sort()
        red, green, blue, alpha = zip(*self)
        r1, r2, g1, g2, b1, b2, a1, a2 = [], [], [], [], [], [], [], []
        for u in unique: # Required to deal with discontinuous colormaps
            for c1, c2, c0 in ((r1, r2, red), (g1, g2, green), (b1, b2, blue), 
                               (a1, a2, alpha)):
                c1.append(c0[positions.index(u)])
                c2.append(c0[::-1][positions[::-1].index(u)])
        color_dict = {'red': zip(positions, r1, r2),
                      'green': zip(positions, g1, g2),
                      'blue': zip(positions, b1, b2),
                      'alpha': zip(positions, a1, a2)}
        return matplotlib.colors.LinearSegmentedColormap(name, color_dict)
    
    def set_colorcycle(self, axis):
        '''Set the color cycle for a matplotlib axis object to the colors in the 
        colorlist
        
        Examples::
        
            >>> from matplotlib import pyplot
            >>> axis = pyplot.subplots(1, 1)[-1]
            >>> clist = colorlist(color('black', 'name'), color('grey', 'name'))
            >>> clist.set_colorcycle(axis)
            >>> axis._get_lines.color_cycle.next()
            [0.0, 0.0, 0.0, 1.0]
        '''
        axis.set_color_cycle(self)
        
    #--- Colorlist transformations:
    def saturate(self, saturation_factor):
        '''Saturate or desaturate all the colors in the list'''
        return self._map('saturate', saturation_factor)
     
    def lighten(self, lighten_factor):
        '''Lighten or darken all the colors in the list'''
        return self._map('lighten', lighten_factor)
     
    def blend(self, other, blendtype = 'mean'):
        '''Blend colors in self with the colors in other. blendtype = 'mean' takes the 
        average in rgb space, blendtype = 'add' takes the sum in rgb space.'''
        return self._map('blend', other, blendtype = blendtype)
     
    def rotate(self, rotation):
        '''Rotate hue for all the colors in the list'''
        return self._map('rotate', rotation)
    
    def dynamic_range(self, dark, bright):
        '''Normalize the lightness values to a range set by dark to bright.
        Use for example to limit Matplotlib colormaps to darker colors
        
        Examples::
        
            >>> from matplotlib import pyplot
            >>> cmap = pyplot.get_cmap('summer')
            >>> clist = rgba2colorlist([cmap(0.0), cmap(1.0)])
            >>> print [round_rgba(c, 1) for c in clist]
            [[0.0, 0.5, 0.4, 1.0], [1.0, 1.0, 0.4, 1.0]]
            >>> clist = clist.dynamic_range(0.25, 0.6)
            >>> print [[round(c, 1) for c in rgba] for rgba in clist]
            [[0.0, 0.5, 0.4, 1.0], [1.0, 1.0, 0.2, 1.0]]
        '''
        lightness_list = self.lightness
        brightest = max(lightness_list)
        darkest = min(lightness_list)
        center = (brightest + darkest)*0.5
        current_range = brightest - darkest
        target_range = bright - dark
        target_center = (bright + dark)*0.5
        range_factor = target_range*1./current_range
        normalized = [(l - center)*range_factor + target_center for l in lightness_list]
        self.lightness = normalized
        return self

    #--- Helper methods:
    @staticmethod
    def _default_positions(n):
        '''Create n evenly spaced floats in the range 0-1
        
        Examples::
        
            >>> print colorlist._default_positions(2)
            [0.0, 1.0]
            >>> print colorlist._default_positions(3)
            [0.0, 0.5, 1.0]
        '''
        return [pos*1./(n - 1) for pos in range(0, n)]
    
    def _map(self, methodname, *args, **kwargs):
        '''Perform a color method on all of the colors in the colorlist
        
        Examples::
        
            >>> clist = colorlist(color((0.0, 0.0, 0.0)), color((0.5, 0.5, 0.5)))
            >>> clist._map('lighten', 0.5)
            [[0.5, 0.5, 0.5, 1.0], [1.0, 1.0, 1.0, 1.0]]
        '''
        return colorlist(*[getattr(col, methodname)(*args, **kwargs) for col in self])
    
    #--- Magic methods:
    def __getattr__(self, name):
        '''Get access to color object attributes
        
        Examples::
            >>> clist = colorlist(color((0.5, 0.5, 0.5)), color((1.0, 1.0, 1.0)))
            >>> print clist.lightness
            [0.5, 1.0]
        '''
        return [getattr(col, name) for col in self]
    
    def __setattr__(self, name, values):
        '''Get access to color object attributes. Attempting to acces a non-
        existent attribute raises an AttributeError.
        
        Inputs:
            * name (str) - attribute name
            * values (str, seq or scalar) - values to be assigned to attribute.
              If values is a sequence other than str, each element of values
              will be applied to a seperate color in the colorlist.
        
        Examples::
            >>> clist = colorlist(color((0.5, 0.5, 0.5)), color((1.0, 1.0, 1.0)))
            >>> clist.lightness = 0.0 # Black out
            >>> print clist
            [[0.0, 0.0, 0.0, 1.0], [0.0, 0.0, 0.0, 1.0]]
            >>> clist.lightness = [0.0, 0.5] # Change the second color to grey
            >>> print clist
            [[0.0, 0.0, 0.0, 1.0], [0.5, 0.5, 0.5, 1.0]]
            >>> clist.red, clist.alpha = 1.0, 0.6 # Add red and make translucent
            >>> print clist
            [[1.0, 0.0, 0.0, 0.6], [1.0, 0.5, 0.5, 0.6]]
            >>> clist.nonexistant_attribute = 1.0 # Change non-existant attribute
            Traceback (most recent call last):
            ...
            AttributeError: 'color' object has no attribute 'nonexistant_attribute'
        '''
        try: 
            len(values) # Works for list, tuple, array, or str
        except TypeError: # Values is a scalar
            values = [values]*len(self) # Repeat n times
        else:
            if str(values) is values: # Values is a string
                values = [values]*len(self) # Repeat n times
        for col, value in zip(self, values):
            if name in col.__class__.__dict__.keys(): # Check that attribute exists
                setattr(col, name, value) # Set attribute for individual color objects
            else: # Unrecognized attribute
                raise AttributeError, "'color' object has no attribute '{0}'".format(name)
    
#--- Convenience functions:
def rgba2colorlist(rgba_list):
    '''Convert a list of rgba tuples into a colorlist object
    
    Examples::
    
        >>> rgba_list = [(0, 0, 0), (1, 1, 1)]
        >>> print rgba2colorlist(rgba_list)
        [[0, 0, 0, 1.0], [1, 1, 1, 1.0]]
    '''
    return colorlist(*[color(rgba) for rgba in rgba_list])

def round_rgba(rgba, pts = 1):
    '''Round elements of rgba tuple to 'pts' decimals'''
    return [round(c, pts) for c in rgba]

#--- Test:
if __name__ == '__main__':
    # Do the doctests
    import doctest
    doctest.testmod() 


