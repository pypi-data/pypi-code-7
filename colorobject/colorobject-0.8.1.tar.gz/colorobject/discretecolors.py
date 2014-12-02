'''
Functions for dealing with colorlists of maximally distinct colors.

Created on Sep 12, 2014

@author: gdelraye
'''

#--- Import packages:
from data import custom_colorsets # Custom lists of maximally distinct colors

#--- Functions for discrete color sets:
def color_cycler(color_list):
    '''
    Cycle indefinitely through list of discrete colors
    color_list can be a list of rgb tuples or a string
    matching an attribute of the custom_colorsets named
    tuple in the module data.
    
    Examples:
    
        >>> print color_cycler('tatarize_269').next() # 1st color is black
        [0.0, 0.0, 0.0, 1.0]
    '''
    if str(color_list) == color_list:
        color_list = getattr(custom_colorsets, color_list)
    index = 0
    n_colors = len(color_list)
    while True:
        yield color_list[index%n_colors]
        index += 1

if __name__ == '__main__':
    import doctest
    doctest.testmod() 

