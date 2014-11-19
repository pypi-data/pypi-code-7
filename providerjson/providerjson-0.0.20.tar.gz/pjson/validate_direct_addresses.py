#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

# Written by Alan Viars
import json, sys, datetime, re


def validate_direct_address_list(l, enumeration_type):
    errors = []
    
    #define a max_length dict
    max_values = {'organization' : 150,
                   'email'       : 150
                 }
    
    #Test for max_length errors    
    i=0
    for d in l:
        
        for k in max_values.keys():
            if d.get(k):
                if max_values[k] < len(str(d.get(k))):
                    error = "%s : %s max allowable length %s." % (d.get('email'),  max_values[k])
                    errors.append(error)
    
        #check for required information
        if not d.get('email'):
            error = "email is required for direct_addresses[%s]." % i
            errors.append(error)
    
        if type(d.get('is_public')) != bool :
            error = "%s : is_public must be true or false." % (d.get('email'))
            errors.append(error)
    
        if not d.get('organization'):
            error = "%s : organization is required." % (d.get('email'))
            errors.append(error)
        i+=1
    
    
    return errors
    
    