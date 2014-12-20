import numpy as np

class Function(object):
    """Abstracts some function algebra"""
    def __call__(self, *args):
        if len(args)>=2:
            self(np.array(args))
        elif len(args)==1:
            value = self.call(args[0])
            if type(value)==np.matrixlib.defmatrix.matrix:
                if value.shape == (1,1):
                    return np.trace(value)
            return value
    def call(self, x):
        """Override this for function evaluation"""
        return 0
