import numpy as np


class Box(object): # pylint: disable=too-few-public-methods
    """Box with utility methods. Intended to abstract operations with the laser bounding box. Eventually I want to make this unnecessary with a more general method for computing maximum time step that uses the actual gaussian beam function and its partials.

    """

    def __init__(self, width, depth, height, center=(0, 0, 0)):
        """Initializes object.

        Args:
          width (float): Box width (x)
          depth (float): Box depth (y)
          height (float): Box height (z)
          center (tuple or np.ndarray): Position of center of the box.

        """

        self.shape = (width/2, depth/2, height/2)
        self.center = center
    def dist(self, point):
        """Calculates distance to box.

        Args:
          point (tuple or np.ndarray): Target point

        Returns:
          float: minimum distance of any point on the box to the target point

        """
        dx_i = lambda i: max(abs(point[i]-self.center[i])-self.shape[i], 0)
        dr = np.array([dx_i(i) for i in range(3)]) # pylint: disable=invalid-name
        return np.sqrt(dr.dot(dr))
    def __contains__(self, point):
        """Test if point is inside of the box.

        Inclusive (boundaries).

        Example:
          Use in keyword to test if the box encloses a point::
            $ box = Box(1.0, 1.0, 1.0)
            $ if (1.0, 0.0, 0.5) in box:
            $   print 'in box'
        """

        return self.dist(point) == 0
