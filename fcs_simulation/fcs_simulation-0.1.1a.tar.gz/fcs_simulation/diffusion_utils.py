
from function import Function
from function_approx import LookupTable, ArrayLookupTable
import numpy as np

NANO = 10**-9
MICRO = 10**-6

# comute timestep from sigma
# TODO: this probably isnt wrong
def time_step(sigma, diffusivity):
    """Calculates dt from sigma.

    Args:
      sigma (float): Width of 3D Gaussian that change in position of a
        diffusing particle would be drawn from after a time interval dt.
      diffusivity (float): Diffusivity of the particle.

    Returns:
      float: time interval, dt, for a diffusing particle to have a mean
        squared distance traveled equal to given sigma

    """
    return sigma**2 / (6*diffusivity)

def sigma_from_dt(dt, diffusivity):
    return np.sqrt(6*diffusivity*dt)


# TODO: This was wrong, might still be
def random_step(position=(0, 0, 0),
                sigma=1.0): # pylint: disable=invalid-name

    """Generates a random brownian step given a timestep size.

    Args:
      position (tuple or np.ndarray): Diffusion source or position
        before step.
      sigma (float): Width of the gaussian

    Returns:
      np.ndarray: New sampled position after time step

    """
    return sigma*np.random.randn(3) + np.array(position)

class Gaussian(Function):
    def __init__(self, sigma=None, mean=None, covariance_matrix=None):
        if mean == None:
            mean = np.zeros(3)
        self.mean = mean
        
        if sigma != None:
            covariance_matrix = np.identity(3)*sigma*sigma
        self.covariance_matrix = np.matrix(covariance_matrix)
        self.covariance_matrix_inv = np.linalg.inv(self.covariance_matrix)

    # this is wrong
    def call(self, position):
        x, y, z = position
        X = np.mat(position - self.mean).T # pylint: disable=invalid-name
        return np.exp(-1/2. * X.T*self.covariance_matrix_inv*X)
        
        # unnecessary normalizing term
        #/np.sqrt((2*np.pi)**3 * np.linalg.det(self.covariance_matrix))


def max_sigma(position, beam_box, min_sigma=1*NANO):
    """Computes the maximum sigma for a particle at position.

    Finds the Gaussian probability density function (pdf) for a
    particle at a given position such that a step drawn from the
    pdf will have an approximately linear path in intensity space.

    Args:
    position (tuple or np.ndarray): Position of the particle

    Returns: float: Maximum sigma corresponding to a Brownian path
      of particle with very small chance of large fluctuations in
      intensity space.
    """

    distance = beam_box.dist(position)
    if distance == 0:
        sigma = 8 * NANO
    else:
        # accuracy * sigma = distance
        sigma = distance/2 + 8 * NANO
    return sigma

class Sigma(Function):
    def __init__(self, r, alpha=0.01*NANO, halflife=100, beta=None):
        if halflife == None:
            halflife = 100
        if beta==None:
            beta = np.log(2)/halflife
        self.r = r
        table_specs = [(-np.sqrt(2)*r, np.sqrt(2)*r, r/100),(-r, r, r/100)]
        self.table = LookupTable(table_specs, initial_value=0)
        self.alpha = alpha
        self.beta = beta
        self.k = int(np.log(10)/self.beta)
        self.N_prime = ArrayLookupTable(table_specs, self.k)
        self.target_deltaI = 0.01
        self.acceptable_overflow = 0.9
    def call(self, position):
        return self.table[position]
    def update(self, position, deltaI):
        multi_index = self.table.getIndex(position)
        self.N_prime[position] = np.roll(self.N_prime[position],1)
#        import ipdb; ipdb.set_trace()
        if abs(deltaI) < self.target_deltaI:
            print 'updating with 1'
            self.N_prime[position][0] = 1
        else:
            print 'updating with 0'
            self.N_prime[position][0] = 0
        deltaSigma = self.alpha*np.sum((self.N_prime[position]-self.acceptable_overflow)*np.exp(-self.beta*np.arange(self.k))) -0.00012*MICRO
        self.table[position] = self.table[position]+deltaSigma
        return self.table[position], deltaSigma, deltaI, abs(deltaI)>self.target_deltaI
