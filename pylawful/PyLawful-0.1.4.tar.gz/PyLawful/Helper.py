#!/bin/python3

import ipaddress

class Helper():

    ##
    ## Operations for variable verification
    ##

    def is_ipv4(self, ip, txt):
        try:
            ipaddress.IPv4Address(ip)
            rc = 1
        except ValueError:
            print('ERROR: %s not a valid IPv4 address' % (txt))
            rc = 0

        return rc

    def is_ipv6(ip, txt):
        try:
            ipaddress.IPv6Address(ip)
            rc = 1
        except ValueError:
            print('ERROR: %s not a valid IPv6 address' % (txt))
            rc = 0

        return rc

    def is_int_range(self, x, low, high, txt):
        if x.isdigit():
            if int(x) >= low and int(x) <= high:
                rc = 1
            else:
                print('ERROR: %s not in valid range: <%s-%s>' % (txt, low, high))
                rc = 0
        else:
            print('ERROR: %s not in right format: <int>, range: <%s-%s>' % (txt, low, high))
            rc = 0

        return rc

    def is_str_length(self, x, low, txt):
        if len(x) >= low:
            rc = 1
        else:
            print('\nERROR: %s min length = %s' % (txt, low))
            rc = 0

        return rc
