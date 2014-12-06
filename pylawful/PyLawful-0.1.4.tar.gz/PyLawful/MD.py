#!/bin/python3

import ipaddress
import Helper

h = Helper.Helper()

class MD():
    cTap2MediationContentId             = ''
    cTap2MediationDestAddressType       = ''
    cTap2MediationDestAddress           = ''
    cTap2MediationDestAddress_hex       = ''
    cTap2MediationDestPort              = ''
    cTap2MediationSrcInterface          = ''
    cTap2MediationDscp                  = ''
    cTap2MediationTimeout               = ''
    cTap2MediationTransport             = ''
    cTap2MediationNotificationEnable    = ''


    def set_tap2_md_data(self):
        # Define Mediation Device
        self.cTap2MediationContentId     = input('\ncTap2MediationContentId      : ')
        self.cTap2MediationDestAddress   = input('cTap2MediationDestAddress    : ')
        self.cTap2MediationDestPort      = input('cTap2MediationDestPort       : ')
        self.cTap2MediationSrcInterface  = input('cTap2MediationSrcInterface   : ')
        self.cTap2MediationDscp          = input('cTap2MediationDscp           : ')

        print('Mediation Timeout (Max 24 days + 1 hour) : ')
        md_year = input('   MD Year     : ')
        md_month = input('   MD Month    : ')
        md_day = input('   MD Day      : ')

        self.cTap2MediationTimeout = self.generate_cTap2MediationTimeout(md_year, md_month, md_day)

    def get_cTap2StreamType(self):
        try:
            if (ipaddress.IPv4Address(self.cTap2MediationDestAddress)):
                self.cTap2MediationDestAddressType = '1'
        except ValueError:
            try:
                if (ipaddress.IPv6Address(self.cTap2MediationDestAddress)):
                    self.cTap2MediationDestAddressType = '2'
            except ValueError:
                self.cTap2MediationDestAddressType = ''

    def validate_MD(self):
        rc = 0

        if self.cTap2MediationDestAddressType is '':
            print('ERROR: Wrong IP addresses used.')
            rc = 1
        if h.is_int_range(self.cTap2MediationContentId, 1, 2147483647, 'CCCid') == 0:
            rc = 1
        if h.is_int_range(self.cTap2MediationDestPort, 1025, 65535, 'MD PORT') == 0:
            rc = 1
        if h.is_int_range(self.cTap2MediationSrcInterface, 0, 2147483647, 'MD SOURCE INT') == 0:
            rc = 1
        if h.is_int_range(self.cTap2MediationDscp, 0, 63, 'MD DSCP') == 0:
            rc = 1
        if self.cTap2MediationTimeout == 0:
            rc = 1

        return rc

    def generate_cTap2MediationTimeout(self, md_year, md_month, md_day):
        rc_year = 0
        rc_month = 0
        rc_day = 0

        if (h.is_int_range(md_year, 2014, 2100, 'MD Year') == 0):
            rc_year = 1
        if (h.is_int_range(md_month, 1, 12, 'MD Month') == 0):
            rc_month = 1
        if (h.is_int_range(md_day, 1, 31, 'MD Day') == 0):
            rc_day = 1

        if (rc_year == 0 and rc_month == 0 and rc_day == 0):
            hex_year = '0x%04x' % (int(md_year))
            hex_month = '0x%02x' % (int(md_month))
            hex_day = '0x%02x' % (int(md_day))
            print('\nMD Timeout will be set to: %s-%s-%s 23:59' % (md_year, md_month, md_day))
            return ('%s%s%s173B0000' % (hex_year.upper()[2:], hex_month.upper()[2:], hex_day.upper()[2:]))
        else:
            return (0)

    def generate_hex(self):
        if self.cTap2MediationDestAddressType == '1':
            temp = self.cTap2MediationDestAddress.split('.')
            temp = "".join([hex(int(value))[2:].zfill(2) for value in temp])
            temp = temp.replace('0x', '')
            self.cTap2MediationDestAddress_hex = temp.upper()
        elif self.cTap2MediationDestAddressType == '2':
            temp = ipaddress.IPv6Address(self.cTap2MediationDestAddress).exploded
            temp = ('').join(temp.split(':'))
            self.cTap2MediationDestAddress_hex = ('').join(temp.split(':'))


