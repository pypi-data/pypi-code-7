'''
Created on: Dec 04, 2014

@author: qwang
'''

def group_user(did, locale):
    '''
    Use did to group user, return number between 1 to 16 as group index.
    '''
    try:
        group = int(did[-1], 16)
        return group + 1
    except:
        # NOTICE if did is not valid, return 0 by default
        return 0
