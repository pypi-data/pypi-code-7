# json does not allow to use tuple for mapping key (see vpar.param_example)
# so, this module offers interoperation between native param and json acceptable param 

import copy

from . import vpar

def param_to_json(native_param):
    """translate native parameter to json assecptable form"""
    d = copy.deepcopy(native_param)
    if 'vpar' in d:
        d['vpar'] = vpar.param_to_json(d['vpar']) 
    return d

def param_from_json(json_param):
    """translate json acceptable data to native form"""
    d = copy.deepcopy(json_param)
    if 'vpar' in d:
        d['vpar'] = vpar.param_from_json(d['vpar']) 
    return d
