#!/bin/python3

import ipaddress
import Helper

h = Helper.Helper()

class TAP():
    cTap2MediationContentId             = ''
    cTap2StreamIndex                    = ''
    cTap2StreamType                     = ''
    citapStreamAddrType                 = ''
    cTap2StreamInterceptEnable          = ''
    citapStreamDestinationAddress       = ''
    citapStreamDestinationAddress_hex   = ''
    citapStreamDestinationLength        = ''
    citapStreamSourceAddress            = ''
    citapStreamSourceAddress_hex        = ''
    citapStreamSourceLength             = ''
    citapStreamVRF                      = ''

    def set_ip_tap_data(self):
        ##
        ## Define Tap
        ##
        self.cTap2MediationContentId         = input('\ncTap2MediationContentId : ')
        self.cTap2StreamIndex                = input('cTap2StreamIndex        : ')
        self.citapStreamDestinationAddress   = input('Dest. Prefix            : ')
        self.citapStreamDestinationLength    = input('Dest. Prefix Length     : ')
        self.citapStreamSourceAddress        = input('Source Prefix           : ')
        self.citapStreamSourceLength         = input('Source Prefix Length    : ')

    def get_cTap2StreamType(self):
        try:
            if (ipaddress.IPv4Address(self.citapStreamDestinationAddress) and ipaddress.IPv4Address(self.citapStreamSourceAddress)):
                self.citapStreamAddrType = '1'
                self.cTap2StreamType = 'ip'
        except ValueError:
            try:
                if (ipaddress.IPv6Address(self.citapStreamDestinationAddress) and ipaddress.IPv6Address(self.citapStreamSourceAddress)):
                    self.citapStreamAddrType = '2'
                    self.cTap2StreamType = 'ip'
            except ValueError:
                self.citapStreamAddrType = ''
                self.cTap2StreamType = ''

    def validate_TAP(self):
        rc = 0

        if self.citapStreamAddrType is '':
            print('ERROR: Wrong or inconsistent IP addresses used.')
            rc = 1
        elif self.citapStreamAddrType is 'ipv4':
            if h.is_int_range(self.cTap2MediationContentId, 1, 2147483647, 'CCCid') == 0:
                rc = 1
            if h.is_int_range(self.cTap2StreamIndex, 1, 2147483647, 'StreamIndex') == 0:
                rc = 1
            if h.is_int_range(self.citapStreamDestinationLength, 0, 32, 'Dest. Pref Len') == 0:
                rc = 1
            if h.is_int_range(self.citapStreamSourceLength, 0, 32, 'Source Pref Len') == 0:
                rc = 1
        elif self.citapStreamAddrType is 'ipv6':
            if h.is_int_range(self.cTap2MediationContentId, 1, 2147483647, 'CCCid') == 0:
                rc = 1
            if h.is_int_range(self.cTap2StreamIndex, 1, 2147483647, 'StreamIndex') == 0:
                rc = 1
            if h.is_int_range(self.citapStreamDestinationLength, 0, 128, 'Dest. Pref Len') == 0:
                rc = 1
            if h.is_int_range(self.citapStreamSourceLength, 0, 128, 'Source Pref Len') == 0:
                rc = 1

        return (rc)

    def generate_hex(self):
        if self.citapStreamAddrType is '1':
            temp = self.citapStreamDestinationAddress.split('.')
            temp = "".join([hex(int(value))[2:].zfill(2) for value in temp])
            temp = temp.replace('0x', '')
            self.citapStreamDestinationAddress_hex = temp.upper()

            temp = self.citapStreamSourceAddress.split('.')
            temp = "".join([hex(int(value))[2:].zfill(2) for value in temp])
            temp = temp.replace('0x', '')
            self.citapStreamSourceAddress_hex = temp.upper()
        elif self.citapStreamAddrType is '2':
            temp = ipaddress.IPv6Address(self.citapStreamDestinationAddress).exploded
            temp = ('').join(temp.split(':'))
            self.citapStreamDestinationAddress_hex = ('').join(temp.split(':'))

            temp = ipaddress.IPv6Address(self.citapStreamSourceAddress).exploded
            temp = ('').join(temp.split(':'))
            self.citapStreamSourceAddress_hex = ('').join(temp.split(':'))


