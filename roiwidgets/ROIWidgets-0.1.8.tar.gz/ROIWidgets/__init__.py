"""ROI Widgets. Create widgets in the ipython notebook that allow user
to select regions of interest from an image.
"""

import os
import PIL
import hashlib
import numpy as np
import math
from IPython import get_ipython
from IPython.html import widgets
from IPython.utils.traitlets import Unicode, Integer, Float, Instance
# import tempfile                         # even though it doesn't work...

def orderedHandles(handles, order, scale):
    """
    Return scaled handles in order.
    """ 
    n = len(order)
    oh = np.zeros((n, 2))
    for i in range(n):
        oh[i] = handles[order[i]]
    return oh/scale

def rectangles(handles):
    """
    Convert rectangle handles to [[left, top], [bottom, right]]
    """
    n = len(handles)
    for i in range(0, n-1, 2):
        left = min(handles[i:i+2, 0])
        right = max(handles[i:i+2, 0])
        top = min(handles[i:i+2, 1])
        bottom = max(handles[i:i+2, 1])
        handles[i:i+2] = [[left, top], [right, bottom]]
    return handles

def circle(handles):
    """
    Convert rectangle handles to circle center and radius.
    """
    rh = rectangles(handles)
    ((left, top), (right, bottom)) = ((rh[0, 0], rh[0, 1]), 
                                      (rh[1, 0], rh[1, 1]))
    print left
    cx = (left + right) / 2.0
    cy = (top + bottom) / 2.0
    rx = (right - cx) * math.sqrt(2.0)
    ry = (bottom - cy) * math.sqrt(2.0)
    return [cx, cy, rx, ry]

class ROIMultiPointWidget(widgets.DOMWidget):
    """
    ROIMultiPoint Widget implements the base functions of all the
    ROIWidgets classes. In a browser it displays as a rectangular view
    of an image. Clicking on the image creates a new handle, which by
    default is displayed as a small blue square. A handle may be
    dragged with the mouse to a new location. Double-clinking a handle
    deletes it. These functions are implemented on the client side in
    javascript and require no action on the server side and no python
    code, except for the Comm code that silently updates widget traits
    as the user manipulates the handles. 

    ROIMultiPointWidget has the following traits:
    description=u'': a unicode string
    imageWidth, imageHeight: dimensions of the input image
    imageURLBase=(u'/static/scratch/': URL of the folder from which
        images are served
    imageURL: URL of the image displayed by this instance. The ROI
        widgets store a possibly reduced-size JPEG version of the
        image in a local scratch directory that can be accessed via
        the ipython notebook server. 
    windowWidth=1024, windowHeight=1024: the maximum dimensions of the
        window used to display the image (and thus the widget
        itself).
    maxScale=1.0: The maximum ratio of the size of the image displayed
        in the widget to the actual size of the image. The image will
        be reduced or enlarged if necessary to fit in the window, but
        it will never be enlarged beyond maxScale. Thus, with default
        values, and image larger than 1024 in either width or height
        will be reduced to display at no larger than 1024 in either
        dimension, but an image smaller than 1024 x 1024 will be
        displayed at actual size. 
    width, height: the actual dimensions of the displayed image
    handleSize=10: Handles are displayed as squares of this size.
    handleAttrs={'stroke': '#000', 'fill': 'blue'}: Used to customize
        the appearance of the handles.
    pathAttrs={'stroke': '#000'}: Used to customize the appearance of
        the path connecting the handles. This trait is not actually
        used by the ROIMultiPointWidget, but is used in subclasses. 
    handles: This trait is the output of the widget. It is a
        dictionary of the form 
        {'handle1': [x1, y1], 'handle2': [x2, y2], ...}
        The x, y coordinates represent locations on the scaled image
        displayed to the user, not the input image. Use the
        scaledHandles method to recover coordinates in original
        coordinates.

        In principle, handles can also be set from the server side to
        manipulate the widget, but this should be done with caution or
        not at all. The keys of the handles object are the ids of DOM
        elements on the client side and must be unique, not just in
        the widget, but in the entire page. 
    """
    _view_name = Unicode('ROIMultiPointWidgetView', sync=True)
    description = Unicode(sync=True)
    imageWidth = Float(sync=True)
    imageHeight = Float(sync=True)
    imageURL = Unicode(sync=True)
    imageURLBase = Unicode(u'/static/scratch/', sync=True)
    width = Integer(sync=True)
    height = Integer(sync=True)
    windowWidth = Integer(1024, sync=True)
    windowHeight = Integer(1024, sync=True)
    maxScale = Float(1.0, sync=True)
    handles = Instance(object, sync=True)
    handleSize = Integer(10, sync=True)
    handleAttrs = Instance(object, sync=True)
    pathAttrs = Instance(object, sync=True)
    
    def __init__(self, 
                 image=None,
                 description=u'',
                 maxScale=1.0,
                 scratchDir=None,
                 imageURLBase=u'/static/scratch/',
                 windowWidth=1024,
                 windowHeight=1024,
                 handleSize=10,
                 handleAttrs={'stroke': '#000', 'fill': 'blue'},
                 pathAttrs={'stroke': '#000'}
    ):
        """
        Create an ROIMultiPointWidget. Parameters:

        image=None: The background image of the widget. This should
            always be supplied.
        scratchDir=<profile_dir> + imageURLBase: The
            directory in which image files should be stored for
            serving to the notebook. These temporary image files
            should in principle be automatically deleted when the
            widget is destroyed, but this doesn't appear to work
            currently.
        description, maxScale=, imageURLBase, windowWidth,
            windowHeight, handleSize, handleAttrs, pathAttrs:
            Initialize values for the corresponding traits. 
        """
        super(ROIMultiPointWidget, self).__init__()
        if (scratchDir):
            self.scratchDir = scratchDir
        else:
            try:
                profileDir = get_ipython().profile_dir.location
                self.scratchDir = profileDir + imageURLBase
            except AttributeError:
                self.scratchDir = (os.environ['HOME'] + 
                    '/.ipython/profile_default' + imageURLBase)
        self.description = description
        self.maxScale = maxScale
        self.imageURLBase = imageURLBase
        self.windowWidth = windowWidth
        self.windowHeight = windowHeight
        self.handleSize = handleSize
        self.handleAttrs = handleAttrs
        self.pathAttrs = pathAttrs
        if (isinstance(image, np.ndarray)):
            image = PIL.Image.fromarray(image)
        self.imageWidth, self.imageHeight = image.size
        self.handles = {};
        self.get_state()
        self.scale = min(
            float(self.windowWidth)/self.imageWidth, 
            float(self.windowHeight)/self.imageHeight,
            self.maxScale
        )
        self.width = int(self.scale * self.imageWidth)
        self.height = int(self.scale * self.imageHeight)
        if (self.scale == 1.0):
            img = image
        else:
            img = image.resize((self.width, self.height), PIL.Image.ANTIALIAS)
        # self.fp = tempfile.NamedTemporaryFile(
        #     suffix='.jpg', prefix='img', dir=self.scratchDir)
        # self.imageFile = self.fp.name
        # img.save(self.fp)
        fname = hashlib.md5(img.tostring()).hexdigest() + '.jpg'
        self.imageFile = os.path.join(self.scratchDir, fname)
        img.save(self.imageFile, format='JPEG')
        self.imageURL = self.imageURLBase + os.path.basename(self.imageFile)
        self.send_state()

    def scaledHandles(self):
        """
        Return the handles in the coordinates of the original
        image. The handle ids are discarded and locations returned as
        an n x 2 numpy array.
        """
        sh = np.array(self.handles.values()) / self.scale
        if sh.shape == (0,):
            # numpy has the notion of a zero-length list of vectors,
            # convenient if you want to do array slicing without
            # having to treat 0 handles as a special case.
            sh = np.zeros((0, 2))
        return sh

    def cleanup(self):
        try:
            os.delete(self.imageFile)
        except OSError:
            pass # ignore nonexistent file error

    def __del__(self):
        self.cleanup()


class ROILineWidget(ROIMultiPointWidget):
    """
    This widget allows the user to draw a line on the image. The first
    click on the image creates two superimposed handles. One of these
    may then be dragged to form the line. No more than two handles may
    be created. 
    """
    _view_name = Unicode('ROILineWidgetView', sync=True)
    
    def __init__(self, *args, **kwargs):
        """
        See ROIMultiPointWidget.
        """
        super(ROILineWidget, self).__init__(*args, **kwargs)


class ROIRectWidget(ROIMultiPointWidget):
    """
    This widget allows the user to delineate a rectangle on the
    image. The first click on the image creates two superimposed
    handles. One of these may then be dragged to form the rectangle,
    which is just the bounding box of the two handles. No more than
    two handles may be created.
    """
    _view_name = Unicode('ROIRectWidgetView', sync=True)
    
    def __init__(self, *args, **kwargs):
        """
        See ROIMultiPointWidget.
        """
        super(ROIRectWidget, self).__init__(*args, **kwargs)

    def scaledHandles(self):
        """
        Return the handles, the upper left and bottom right corners of
        the rectangle, in the coordinates of the original image. The
        handle ids are discarded and locations returned as a 2 x 2
        numpy array. Coordinates are rearranged if necessary into the
        form [[left, top], [right, bottom]].
        """
        sh = super(ROIRectWidget, self).scaledHandles()
        return rectangles(sh)


class ROIMultiRectWidget(ROIMultiPointWidget):
    """
    This widget allows the user to delineate a rectangle on the
    image. The first click on the image creates two superimposed
    handles. One of these may then be dragged to form the rectangle,
    which is just the bounding box of the two handles. No more than
    two handles may be created.
    """
    _view_name = Unicode('ROIMultiRectWidgetView', sync=True)
    handleOrder = Instance(object, sync=True)
    
    def __init__(self, *args, **kwargs):
        """
        See ROIMultiPointWidget.
        """
        super(ROIMultiRectWidget, self).__init__(*args, **kwargs)
        self.handleOrder = []
        self.send_state()

    def scaledHandles(self):
        """
        Return the handles, the upper left and bottom right corners of
        the rectangle, in the coordinates of the original image. The
        handle ids are discarded and locations returned as a 2 x 2
        numpy array. Coordinates are rearranged if necessary into the
        form [[left, top], [right, bottom]].
        """
        sh = orderedHandles(self.handles, self.handleOrder, self.scale)
        return rectangles(sh)


class ROIEllipseWidget(ROIMultiPointWidget):
    """
    This widget allows the user to delineate an ellipse on the
    image. The first click on the image creates two superimposed
    handles. One of these may then be dragged to form the ellipse,
    which is inscribed in the bounding box of the two handles. No more
    than two handles may be created.
    """
    _view_name = Unicode('ROIEllipseWidgetView', sync=True)
    
    def __init__(self, *args, **kwargs):
        """
        See ROIMultiPointWidget.
        """
        super(ROIEllipseWidget, self).__init__(*args, **kwargs)

    def scaledHandles(self):
        """
        Return the handles, the upper left and bottom right corners of
        the ellipse, in the coordinates of the original image. The
        handle ids are discarded and locations returned as a 2 x 2
        numpy array. Coordinates are rearranged if necessary into the
        form [[left, top], [right, bottom]].
        """
        sh = super(ROIEllipseWidget, self).scaledHandles()
        return rectangles(sh)

    def centerRadius(self):
        """
        Return the center and semi-major axes of the ellipse as an
        ndarray [cx, cy, rx, ry].
        """
        sh = self.scaledHandles()
        return np.ndarray(circle(sh))


class ROIMultiEllipseWidget(ROIMultiPointWidget):
    """
    This widget allows the user to delineate a ellipse on the
    image. The first click on the image creates two superimposed
    handles. One of these may then be dragged to form the ellipse,
    which is just the bounding box of the two handles. No more than
    two handles may be created.
    """
    _view_name = Unicode('ROIMultiEllipseWidgetView', sync=True)
    handleOrder = Instance(object, sync=True)
    
    def __init__(self, *args, **kwargs):
        """
        See ROIMultiPointWidget.
        """
        super(ROIMultiEllipseWidget, self).__init__(*args, **kwargs)
        self.handleOrder = []
        self.send_state()

    def scaledHandles(self):
        """
        Return the handles, the upper left and bottom right corners of
        the ellipse, in the coordinates of the original image. The
        handle ids are discarded and locations returned as a 2 x 2
        numpy array. Coordinates are rearranged if necessary into the
        form [[left, top], [right, bottom]].
        """
        sh = orderedHandles(self.handles, self.handleOrder, self.scale)
        return rectangles(sh)

    def centerRadius(self):
        """
        Return the centers and semi-major axes of the ellipses as an n
        x 4 ndarray [[cx0, cy0, rx0, ry0], ...].
        """
        sh = self.scaledHandles()
        n = len(sh)
        c = []
        for i in range(0, n-1, 2):
            c.append(circle(sh[i:i+2]))
        return c

class ROIPolygonWidget(ROIMultiPointWidget):
    """
    This widget allows the user to draw a polygon. It behaves
    identically to the ROIMultiPointWidget, except that the handles
    are joined by lines to form a polygon. It has an additional output
    trait, handleOrder, an array of handle ids corresponding to those
    in handles. This specifies the order in which they are joined to
    form the polygon.
    """
    _view_name = Unicode('ROIPolygonWidgetView', sync=True)
    handleOrder = Instance(object, sync=True)
    
    def __init__(self, *args, **kwargs):
        super(ROIPolygonWidget, self).__init__(*args, **kwargs)
        self.handleOrder = []
        self.send_state()

    def scaledHandles(self):
        """
        Return the handles in the coordinates of the original
        image. The handle ids are discarded and locations returned as
        an n x 2 numpy array. The handles are in the correct order. 
        """
        return orderedHandles(self.handles, self.handleOrder, self.scale)
