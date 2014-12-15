import inspect, PIL, sys, cv2, hashlib, os
from cStringIO import StringIO
from functools import total_ordering
from IPython import get_ipython
# do this before importing pylab or pyplot
import matplotlib
matplotlib.use('Agg')
# Now it's safe
import matplotlib.pyplot as plt
import numpy as np
from IPython.html.widgets import HTMLWidget
from IPython.utils.traitlets import Unicode

def argNames(*args):
    """
    Get the names of the argument for a function

    Returns:
    --------
    A set whose members are the argument names
    
    Parameters:
    -----------
    func1, func2, ... -- the functions to be analyzed. The arguments
        are discovered by inspecting func. In addition, if
        func.argNames is defined, it is called (without arguments) to
        get a list of addition names. Any number of functions may be
        listed. If func is a class, func.__init__ is used
        instead. 'self' is always removed from the argument list.
    """
    names = set({})
    for a in args:
        try:
            func = a
            spec = inspect.getargspec(func)
        except TypeError:
            func = a.__init__
            spec = inspect.getargspec(func)
        names |= set(spec.args)
        try:
            names |= set(func.argNames())
        except AttributeError:
            pass
    names.discard('self')
    return(names)

def filterArgs(func, **kwargs):
    """
    Select keyword arguments for a function
    """
    args = argNames(func)
    ks = set(kwargs.keys())
    ks.discard('self')
    kinc = ks & args
    kexc = ks - args
    inc = {k: kwargs[k] for k in kinc}
    exc = {k: kwargs[k] for k in kexc}
    return(inc, exc)

class Error(Exception):
    def __init__(self, value):
        super(Error, self).__init__(value)
        self.value = value
        
    def str(self):
        return repr(self.value)

    def repr(self):
        return repr(self.value)


class PlotToImage(object):
    """
    PlotToImage is a context manager for capturing a matplotlib plot
    as an Image. Typical use:

    with PlotToImage() as pti:
        do some plotting...

    pti.image is a PIL.Image of the results, or None if the plot
    failed.

    Parameters:
    -----------
    figure: If supplied, this is the matplotlib.pyplot.figure into which
        plotting will be done. If not supplied, PlotToImage assumes
        the code to follow will create the figure and leave it as the
        current figure. In either case, pti.fig will be the figure. 
    format='jpg': The format of the intermediate image file
    """
    def __init__(self, figure=None, format='jpg'):
        self.format = format
        self.fig = figure
        self.image = None

    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        imgdata = StringIO()
        self.fig = self.fig or plt.gcf()
#        self.fig.savefig(imgdata, format=self.format, bbox_inches='tight')
        self.fig.savefig(imgdata, format=self.format)
        imgdata.seek(0)
        self.image = PIL.Image.open(imgdata)


class Capturing(list):
    """
    Capturing is a context manager for capturing output to
    stdout. Typical use:

    with Capturing() as output:
        do_something(args)

    output is now a list containing the lines printed by do_something.

    Based on http://stackoverflow.com/questions/16571150/how-to-capture-stdout-output-from-a-python-function-call
    """
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout


@total_ordering
class Interval(object):
    """
    Interval(a, b) represents the set of real numbers {x: a <= x <= b}. 
    Interval I is less than Interval J if x <= y for every (x, y) in 
    I x J and x < y for some (x, y) in I x J. (The last qualification
    excludes the case [x, x] < [x, x].) Although the class is intended
    for numbers, it will work for any objects that have an __lt__
    method. This is not a total order, since it is possible to have 
    I = K, J = K, I < J, e.g. I = [0, 1], J = [1, 2], K = [0, 2].
    """
    
    def __init__(self, lb, ub):
        """
        Create the Interval [lb, ub]
        
        Parameters:
        -----------
        lb: the inclusive lower bound
        ub: the exclusive upper bound
        """
        if (ub < lb):
            raise Error("Upper bound less than lower bound")
        self.lb, self.ub = lb, ub
        
    def __lt__(self, J):
        return not J.lb < self.ub and (self.lb < J.ub or J.lb < J.ub)
    
    def __eq__(self, J):
        return not self < J and not J < self

    def __repr__(self):
        name = self.__class__.__name__
        f = '{name}({lb}, {ub})'
        return f.format(name=name, lb=self.lb, ub=self.ub)
        
    @classmethod
    def test_cmp(cls):
        """Return True if comparisons work right."""
        desired_results = [True, False, True, True, False, True, True, 
                           False, True, True, False]
        results = [
            cls(0, 1) < cls(1, 2),
            cls(0, 2) < cls(1, 3),
            cls(0, 2) == cls(1, 3),
            cls(0, 2) <= cls(1, 3),
            cls(0, 2) > cls(1, 3),
            cls(0, 2) >= cls(1, 3),
            cls(0, 1) < cls(1, 1),
            cls(1, 1) < cls(1, 1),
            cls(1, 1) == cls(1, 1),
            cls(1, 1) < cls(2, 2),
            cls(1, 1) == cls(2, 2),
        ]
        return all(x == y for x, y in zip(results, desired_results))


@total_ordering
class Rectangle(object):
    """
    Rectangle([x0, x1], [y0, y1]) represents the set
    {(x, y): x0 <= x <= x1 and y0 <= y <= y1}. The class was created to allow
    an ordering of rectangles in a grid first by rows, then by columns.
    Rectangles are ordered lexicographically first by y, then by x.
    """
    
    def __init__(self, xs, ys):
        """
        Create a Rectangle.
        
        Parameters:
        -----------
        xs: an array or tuple of the x lower and upper bounds
        ys: an array or tuple of the y lower and upper bounds
        """
        x0, x1 = xs
        y0, y1 = ys
        self.xi = Interval(x0, x1)
        self.yi = Interval(y0, y1)

    def __repr__(self):
        name = self.__class__.__name__
        f = '{name}(({x0}, {x1}), ({y0}, {y1}))'
        return f.format(
            name=name,
            x0=self.xi.lb, x1=self.xi.ub,
            y0=self.yi.lb, y1=self.yi.ub
        )

    def __eq__(self, J):
        return self.xi == J.xi and self.yi == J.yi
    
    def __lt__(self, J):
        return self.yi < J.yi or (self.yi == J.yi and self.xi < J.xi)

    
def firstFrame(videoFile):
    """
    Return the first frame of a video file as an image
    """
    video = cv2.VideoCapture(videoFile)
    if not video.isOpened():
        raise Error('Unable to open video file ' + videoFile)
    success, firstFrame = video.read()
    if not success:
        raise Error('Unable to read video file ' + videoFile)
    video.release()
    return(firstFrame)


class HTMLImageWidget(HTMLWidget):
    description = Unicode(sync=True)
    value = Unicode(sync=True)
    
    def __init__(
        self,
        image,
        description=u'',
        maxHeight=512,
        maxWidth=512,
        maxScale=1.0,
        scratchDir=None,
        imageURLBase=u'/static/scratch/',
        autoEnhance=True,
        **kwargs
    ):
        super(HTMLImageWidget, self).__init__(
            description=description,
            **kwargs
        )
        self.setImage(
            image=image,
            description=description,
            maxHeight=maxHeight,
            maxWidth=maxWidth,
            maxScale=maxScale,
            scratchDir=scratchDir,
            imageURLBase=imageURLBase,
            autoEnhance=autoEnhance
        )
        
    __init__.argNames = lambda: argNames(HTMLWidget)

    def setImage(
        self,
        image,
        description=u'',
        maxHeight=512,
        maxWidth=512,
        maxScale=1.0,
        scratchDir=None,
        imageURLBase=u'/static/scratch/',
        autoEnhance=True,
    ):
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
        self.maxWidth = maxWidth
        self.maxHeight = maxHeight
        if (isinstance(image, np.ndarray)):
            image = PIL.Image.fromarray(image.astype('uint8'))
        self.imageWidth, self.imageHeight = image.size
        self.scale = min(
            float(self.maxWidth)/self.imageWidth, 
            float(self.maxHeight)/self.imageHeight,
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
        if autoEnhance:
            img = self.enhance(img)
        fname = hashlib.md5(img.tostring()).hexdigest() + '.jpg'
        self.imageFile = os.path.join(self.scratchDir, fname)
        img.save(self.imageFile, format='JPEG')
        self.imageURL = self.imageURLBase + os.path.basename(self.imageFile)
        self.html = u'<img src="'
        self.html += self.imageURL
        self.html += u'" alt="' + description
        self.html += u'">'
        self.value = self.html
        self.send_state('value')
        
    def enhance(self, img):
        gsimg = img.convert('L')
        gsnpimg = np.array(gsimg)
        mx = gsnpimg.max()
        mn = gsnpimg.min()
        if mx == mn:
            return(img)
        b = 255.0/(mx - mn)
        npimg = np.array(img)
        npimg = b * (npimg - mn)
        npimg = npimg.astype('uint8')
        img = PIL.Image.fromarray(npimg)
        return img

