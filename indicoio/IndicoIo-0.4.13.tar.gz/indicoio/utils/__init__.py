import inspect, json, getpass, os
import requests
import numpy as np
from skimage.transform import resize

from indicoio import JSON_HEADERS

def auth_query():
    email = os.environ.get("INDICO_EMAIL")
    password = os.environ.get("INDICO_PASSWORD")

    # store settings
    if not email:
        email = raw_input("Email: ")
        os.environ["INDICO_EMAIL"] = email

    if not password:
        password = getpass.getpass("Password: ")
        os.environ["INDICO_PASSWORD"] = password

    return (email, password)

def api_handler(arg, url, batch=False, auth=None, **kwargs):
    data = {'data': arg}
    data.update(**kwargs)
    json_data = json.dumps(data)
    if batch:
        url += "/batch"
        if not auth:
            auth = auth_query()
    response = requests.post(url, data=json_data, headers=JSON_HEADERS, auth=auth).json()
    results = response.get('results', False)
    if results is False:
        error = response.get('error')
        raise ValueError(error)
    return results

class TypeCheck(object):
    """
    Decorator that performs a typecheck on the input to a function
    """
    def __init__(self, accepted_structures, arg_name):
        """
        When initialized, include list of accepted datatypes and the
        arg_name to enforce the check on. Can totally be daisy-chained.
        """
        self.accepted_structures = accepted_structures
        self.is_accepted = lambda x: type(x) in accepted_structures
        self.arg_name = arg_name

    def __call__(self, fn):
        def check_args(*args, **kwargs):
            arg_dict = dict(zip(inspect.getargspec(fn).args, args))
            full_args = dict(arg_dict.items() + kwargs.items())
            if not self.is_accepted(full_args[self.arg_name]):
                raise DataStructureException(
                    fn,
                    full_args[self.arg_name],
                    self.accepted_structures
                )
            return fn(*args, **kwargs)
        return check_args


class DataStructureException(Exception):
    """
    If a non-accepted datastructure is passed, throws an exception
    """
    def __init__(self, callback, passed_structure, accepted_structures):
        self.callback = callback.__name__
        self.structure = str(type(passed_structure))
        self.accepted = [str(structure) for structure in accepted_structures]

    def __str__(self):
        return """
        function %s does not accept %s, accepted types are: %s
        """ % (self.callback, self.structure, str(self.accepted))


@TypeCheck((list, dict, np.ndarray), 'array')
def normalize(array, distribution=1, norm_range=(0, 1), **kwargs):
    """
    First arg is an array, whether that's in the form of a numpy array,
    a list, or a dictionary that contains the data in its values.

    Second arg is the desired distribution which would be applied before
    normalization.
        Supports linear, exponential, logarithmic and raising to whatever
        power specified (in which case you just put a number)

    Third arg is the range across which you want the data normalized
    """
    # Handling dictionary array input
    # Note: lists and numpy arrays behave the same in this program
    dict_array = isinstance(array, dict)

    if dict_array:
        keys = array.keys()
        array = np.array(array.values()).astype('float')
    else:  # Decorator errors if this isn't a list or a numpy array
        array = np.array(array).astype('float')

    # Handling various distributions
    if type(distribution) in [float, int]:
        array = np.power(array, distribution)
    else:
        array = getattr(np, distribution)(array, **kwargs)

    # Prep for normalization
    x_max, x_min = (np.max(array), np.min(array))

    def norm(element,x_min,x_max):
        base_span = (element - x_min)*(norm_range[-1] - norm_range[0])
        return norm_range[0] + base_span / (x_max - x_min)

    norm_array = np.vectorize(norm)(array, x_min, x_max)

    if dict_array:
        return dict(zip(keys, norm_array))
    return norm_array

def image_preprocess(image):
    """
    Takes an image and prepares it for sending to the api including 
    resizing and image data/structure standardizing.
    """
    if isinstance(image,list):
        image = np.asarray(image)
    if type(image).__module__ != np.__name__:
        raise ValueError('Image was not of type numpy.ndarray or list.')
    if str(image.dtype) in ['int64','uint8']:
        image = image/255.
    if len(image.shape) == 2:
        image = np.dstack((image,image,image))
    if len(image.shape) == 4:
        image = image[:,:,:3]
    image = resize(image,(64,64))
    image = image.tolist()
    return image