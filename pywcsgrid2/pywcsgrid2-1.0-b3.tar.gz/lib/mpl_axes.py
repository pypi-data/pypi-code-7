import mpl_toolkits.axes_grid1 as axes_grid1
import warnings
from mpl_toolkits.axes_grid1.mpl_axes import (SimpleChainedObjects,
                                              SimpleAxisArtist)
import matplotlib.axes as maxes

import six


class AxesBase(object):
    def toggle_axisline(self, b):
        warnings.warn("toggle_axisline is not necessary and deprecated in axes_grid1")

    class AxisDict(dict):
        def __init__(self, axes):
            self.axes = axes
            super(AxesBase.AxisDict, self).__init__()

        def __getitem__(self, k):
            if isinstance(k, tuple):
                r = SimpleChainedObjects([dict.__getitem__(self, k1) for k1 in k])
                return r
            elif isinstance(k, slice):
                if k.start == None and k.stop == None and k.step == None:
                    r = SimpleChainedObjects(list(six.itervalues(self)))
                    return r
                else:
                    raise ValueError("Unsupported slice")
            else:
                return dict.__getitem__(self, k)

        def __call__(self, *v, **kwargs):
            return maxes.Axes.axis(self.axes, *v, **kwargs)


    def __init__(self, *kl, **kw):
        self._axes_class.__init__(self, *kl, **kw)



    def _init_axis_artists(self, axes=None):
        if axes is None:
            axes = self

        self._axislines = self.AxisDict(self)

        self._axislines["bottom"] = SimpleAxisArtist(self.xaxis, 1, self.spines["bottom"])
        self._axislines["top"] = SimpleAxisArtist(self.xaxis, 2, self.spines["top"])
        self._axislines["left"] = SimpleAxisArtist(self.yaxis, 1, self.spines["left"])
        self._axislines["right"] = SimpleAxisArtist(self.yaxis, 2, self.spines["right"])


    def _get_axislines(self):
        return self._axislines

    axis = property(_get_axislines)

    def cla(self):

        self._axes_class.cla(self)
        self._init_axis_artists()


_axes_classes = {}


def axes_class_factory(axes_class=None):
    # This makes a new class that inherits from SubplotBase and the
    # given axes_class (which is assumed to be a subclass of Axes).
    # This is perhaps a little bit roundabout to make a new class on
    # the fly like this, but it means that a new Subplot class does
    # not have to be created for every type of Axes.
    if axes_class is None:
        axes_class = maxes.Axes

    new_class = _axes_classes.get(axes_class)
    if new_class is None:
        new_class = type(str("%sSubplot") % (axes_class.__name__),
                         (AxesBase, axes_class),
                         {'_axes_class': axes_class})
        _axes_classes[axes_class] = new_class

    return new_class

# This is provided for backward compatibility
Axes = axes_class_factory()
