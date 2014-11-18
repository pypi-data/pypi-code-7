#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

# Written by Alan Viars
import json, sys, datetime, re
from choices import TAXONOMY_CODES

def validate_taxonomy_list(l, enumeration_type):
    errors = []
    primary_count  = 0

    for d in l:

        #check for required information
        if d.get('code') not in TAXONOMY_CODES:
            error = "%s : code (taxonomy) is not a valide taxonomy code. See http://www.wpc-edi.com/taxonomy" % d.get('code')
            errors.append(error)

        if type(d.get('primary')) != type(True) :
            error = "%s : primay must be true or false." % (d.get('code'))
            errors.append(error)

        if d.get('primary') == True:
            primary_count += 1
    # check that only one taxonomy is marked as primary

    if primary_count != 1:
        error = "Exactly 1 taxonomy code must be marked as primary. The primary count is %s." % (primary_count)
        errors.append(error)



    return errors

