#!/bin/python3

#1.3.6.1.4.1.9.9.399
#1.3.6.1.4.1.9.9.394

from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902
import MD, TAP, Helper
import getpass

h = Helper.Helper()
cmdGen = cmdgen.CommandGenerator()
target = '0.0.0.0'
security = ''

##
## Operations for SNMP generation and printing
##


def print_walk(errorIndication, errorStatus, errorIndex, varBinds):
    global target

    print(' ')
    if errorIndication:
        print('(%s) : errorIndication = %s' % (
            target,
            errorIndication
        )
        )
        if str(errorIndication) == 'No SNMP response received before timeout':
            print('\nPlease verify:')
            print('1. Target IP is correct.')
            print('2. Target IP is reachable.')
            print('3. LI and SNMPv3 are active on the target router.')
        if str(errorIndication) == 'unknownUserName':
            print('\nPlease verify:')
            print('1. SNMPV3 credentials are correct.')
            print('2. SNMPV3 is enabled on target router.')
    else:
        if errorStatus:
            print('RX (%s) : errorStatus = %s at %s' % (
                target,
                errorStatus.prettyPrint(),
                errorIndex and varBinds[int(errorIndex) - 1] or '?'
            )
            )
        else:
            for elem in varBinds:
                for name, val in elem:
                    print('RX (%s) : %s = %s' % (target, name.prettyPrint(), val.prettyPrint()))


def print_response(errorIndication, errorStatus, errorIndex, varBinds):
    global target

    print(' ')
    if errorIndication:
        print(errorIndication)
    else:
        if errorStatus:
            print('RX (%s) : errorStatus = %s at %s' % (
                target,
                errorStatus.prettyPrint(),
                errorIndex and varBinds[int(errorIndex) - 1] or '?'
            )
            )
        else:
            for elem in varBinds:
                name = elem[0]
                val = elem[1]
                print('RX (%s) : %s = %s' % (target, name.prettyPrint(), val.prettyPrint()))


def print_set(oids):
    global target

    print('')
    for elem in oids:
        print('TX (%s) : %s' % (target, elem))


def send_walk(OID):
    global target

    errorIndication, errorStatus, errorIndex, varBinds = cmdGen.nextCmd(
        security,
        cmdgen.UdpTransportTarget((target, 161)),
        OID
    )
    print_walk(errorIndication, errorStatus, errorIndex, varBinds)


def send_snmp_set(oids):
    global target
    print_set(oids)

    ## Need this check, because setting single OID single 'tuple', not 'tuple' of tuples

    if type(oids[0]) == tuple:
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.setCmd(
            security,
            cmdgen.UdpTransportTarget((target, 161)),
            *oids
        )
    elif type(oids[0]) == str:
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.setCmd(
            security,
            cmdgen.UdpTransportTarget((target, 161)),
            oids
        )

    print_response(errorIndication, errorStatus, errorIndex, varBinds)


def walk_mibs():

    if not check_config():
        return

    print('\nPolling: ciscoTap2MIB')
    send_walk('1.3.6.1.4.1.9.9.399')

    print('\nPolling: ciscoIpTapMIB')
    send_walk('1.3.6.1.4.1.9.9.394')



##
## Operations for creating and deleting Mediation Device data in CISCO-TAP2-MIB
##

def tap2_md():
    if not check_config():
        return

    rc = 1
    md = MD.MD()
    while rc == 1:
        md.set_tap2_md_data()
        md.get_cTap2StreamType()
        rc = md.validate_MD()

    md.generate_hex()
    tap2_md_create(md)

def tap2_md_create(md):
    oids = (
        ('1.3.6.1.4.1.9.9.399.1.1.2.1.2.' + md.cTap2MediationContentId, rfc1902.Integer(md.cTap2MediationDestAddressType)),
        ('1.3.6.1.4.1.9.9.399.1.1.2.1.3.' + md.cTap2MediationContentId, rfc1902.OctetString(hexValue=md.cTap2MediationDestAddress_hex)),
        ('1.3.6.1.4.1.9.9.399.1.1.2.1.4.' + md.cTap2MediationContentId, rfc1902.Unsigned32(md.cTap2MediationDestPort)),
        ('1.3.6.1.4.1.9.9.399.1.1.2.1.5.' + md.cTap2MediationContentId, rfc1902.Integer(md.cTap2MediationSrcInterface)),
        ('1.3.6.1.4.1.9.9.399.1.1.2.1.7.' + md.cTap2MediationContentId, rfc1902.Integer(md.cTap2MediationDscp)),
        ('1.3.6.1.4.1.9.9.399.1.1.2.1.10.' + md.cTap2MediationContentId, rfc1902.OctetString(hexValue=md.cTap2MediationTimeout)),
        ('1.3.6.1.4.1.9.9.399.1.1.2.1.11.' + md.cTap2MediationContentId, rfc1902.Integer(1)),
        ('1.3.6.1.4.1.9.9.399.1.1.2.1.13.' + md.cTap2MediationContentId, rfc1902.Integer(4))
    )
    send_snmp_set(oids)


def tap2_md_delete():
    cTap2MediationContentId = input('\ncTap2MediationContentId : ')

    oids = (
        ('1.3.6.1.4.1.9.9.399.1.1.2.1.13.' + cTap2MediationContentId, rfc1902.Integer(6))
    )
    send_snmp_set(oids)


##
## Operations for creating, activating and deleting CISCO-IP-TAP streams.
##

def ip_tap():
    if not check_config():
        return

    rc = 1
    tap = TAP.TAP()
    while rc == 1:
        tap.set_ip_tap_data()
        tap.get_cTap2StreamType()
        rc = tap.validate_TAP()

    tap.generate_hex()
    ip_tap_create(tap)
    ip_tap_activate(tap)


def ip_tap_create(tap):
    oids = (
        ('1.3.6.1.4.1.9.9.394.1.1.2.1.1.' + tap.cTap2MediationContentId + '.' + tap.cTap2StreamIndex, rfc1902.Integer(0)),
        ('1.3.6.1.4.1.9.9.394.1.1.2.1.2.' + tap.cTap2MediationContentId + '.' + tap.cTap2StreamIndex, rfc1902.Integer(int(tap.citapStreamAddrType))),
        ('1.3.6.1.4.1.9.9.394.1.1.2.1.3.' + tap.cTap2MediationContentId + '.' + tap.cTap2StreamIndex, rfc1902.OctetString(hexValue=tap.citapStreamDestinationAddress_hex)),
        ('1.3.6.1.4.1.9.9.394.1.1.2.1.4.' + tap.cTap2MediationContentId + '.' + tap.cTap2StreamIndex, rfc1902.Unsigned32(int(tap.citapStreamDestinationLength))),
        ('1.3.6.1.4.1.9.9.394.1.1.2.1.5.' + tap.cTap2MediationContentId + '.' + tap.cTap2StreamIndex, rfc1902.OctetString(hexValue=tap.citapStreamSourceAddress_hex)),
        ('1.3.6.1.4.1.9.9.394.1.1.2.1.6.' + tap.cTap2MediationContentId + '.' + tap.cTap2StreamIndex, rfc1902.Unsigned32(int(tap.citapStreamSourceLength))),
        ('1.3.6.1.4.1.9.9.394.1.1.2.1.7.' + tap.cTap2MediationContentId + '.' + tap.cTap2StreamIndex, rfc1902.Integer(0)),
        ('1.3.6.1.4.1.9.9.394.1.1.2.1.8.' + tap.cTap2MediationContentId + '.' + tap.cTap2StreamIndex, rfc1902.Integer(0)),
        ('1.3.6.1.4.1.9.9.394.1.1.2.1.16.' + tap.cTap2MediationContentId + '.' + tap.cTap2StreamIndex, rfc1902.Integer(4))
    )
    send_snmp_set(oids)


def ip_tap_activate(tap):
    oids = (
        ('1.3.6.1.4.1.9.9.399.1.2.1.1.2.' + tap.cTap2MediationContentId + '.' + tap.cTap2StreamIndex, rfc1902.Integer(1)),
        ('1.3.6.1.4.1.9.9.399.1.2.1.1.3.' + tap.cTap2MediationContentId + '.' + tap.cTap2StreamIndex, rfc1902.Integer(1)),
        ('1.3.6.1.4.1.9.9.399.1.2.1.1.6.' + tap.cTap2MediationContentId + '.' + tap.cTap2StreamIndex, rfc1902.Integer(4))
    )
    send_snmp_set(oids)


def ip_tap_delete():
    cTap2MediationContentId = input('\ncTap2MediationContentId : ')
    cTap2StreamIndex        = input('cTap2StreamIndex        : ')

    oids = (
        ('1.3.6.1.4.1.9.9.399.1.2.1.1.6.' + cTap2MediationContentId + '.' + cTap2StreamIndex, rfc1902.Integer(6)),
    )
    send_snmp_set(oids)

    oids = (
        ('1.3.6.1.4.1.9.9.394.1.1.2.1.16.' + cTap2MediationContentId + '.' + cTap2StreamIndex, rfc1902.Integer(6)),
    )
    send_snmp_set(oids)



##
## Operations for monitoring
##


def list_taps():
    global target
    taps = []

    oids = '1.3.6.1.4.1.9.9.399.1.2.1.1.2'

    errorIndication, errorStatus, errorIndex, varBinds = cmdGen.nextCmd(
        security,
        cmdgen.UdpTransportTarget((target, 161)),
        oids
    )
    if errorIndication:
        print(errorIndication)
    else:
        if errorStatus:
            print('%s at %s' % (
                errorStatus.prettyPrint(),
                errorIndex and varBinds[int(errorIndex) - 1] or '?'
            )
            )
        else:
            for elem in varBinds:
                for name, val in elem:
                    data = name.prettyPrint()
                    data = data.split('.')
                    taps.append(data[14] + '.' + data[15])

    if len(taps) > 0:
        print('\nThe following TAP\'s are set: ')
        for elem in taps:
            print(elem)
    else:
        print('\nNo TAPs found.')

def show_intercept_counters():
    send_walk('1.3.6.1.4.1.9.9.399.1.2.1.1.4')


##
## Operations to ensure basic operations.
##

def set_target():
    global target

    while True:
        ip = input('\nEnter IP          : ')

        if h.is_ipv4(ip, ip):
            target = ip
            break

def set_snmp_security():
    global security

    selection = '1'

    while selection:
        print('\n####################################################')
        print('    1. AuthNoPriv: MD5')
        print('    2. AuthNoPriv: SHA')
        print('    3. AuthPriv  : MD5, DES')
        print('    4. AuthPriv  : MD5, 3DES')
        print('    5. AuthPriv  : MD5, AES')
        print('    6. AuthPriv  : SHA, DES')
        print('    7. AuthPriv  : SHA, 3DES')
        print('    8. AuthPriv  : SHA, AES')
        print('    0. Exit')

        selection = input('\nSelect option: ')

        if selection == '1':
            username = input('\nUsername    : ')
            authpass = getpass.getpass('MD5 Password: ')
            if h.is_str_length(username, 1, 'Username') and h.is_str_length(authpass, 8, 'AuthPass'):
                security = cmdgen.UsmUserData(username, authKey=authpass, authProtocol=cmdgen.usmHMACMD5AuthProtocol,
                                              privProtocol=cmdgen.usmNoPrivProtocol)
                return
        elif selection == '2':
            username = input('\nUsername    : ')
            authpass = getpass.getpass('SHA Password: ')
            if h.is_str_length(username, 1, 'Username') and h.is_str_length(authpass, 8, 'AuthPass'):
                security = cmdgen.UsmUserData(username, authKey=authpass, authProtocol=cmdgen.usmHMACSHAAuthProtocol,
                                              privProtocol=cmdgen.usmNoPrivProtocol)
                return
        elif selection == '3':
            username = input('\nUsername    : ')
            authpass = getpass.getpass('MD5 Password: ')
            privpass = getpass.getpass('DES Password: ')
            if h.is_str_length(username, 1, 'Username') and h.is_str_length(authpass, 8, 'AuthPass') and h.is_str_length(
                    privpass, 8, 'PrivPass'):
                security = cmdgen.UsmUserData(username, authKey=authpass, authProtocol=cmdgen.usmHMACMD5AuthProtocol,
                                              privKey=privpass, privProtocol=cmdgen.usmDESPrivProtocol)
                return
        elif selection == '4':
            username = input('\nUsername     : ')
            authpass = getpass.getpass('MD5 Password : ')
            privpass = getpass.getpass('3DES Password: ')
            if h.is_str_length(username, 1, 'Username') and h.is_str_length(authpass, 8, 'AuthPass') and h.is_str_length(
                    privpass, 8, 'PrivPass'):
                security = cmdgen.UsmUserData(username, authKey=authpass, authProtocol=cmdgen.usmHMACMD5AuthProtocol,
                                              privKey=privpass, privProtocol=cmdgen.usm3DESEDEPrivProtocol)
                return
        elif selection == '5':
            username = input('\nUsername    : ')
            authpass = getpass.getpass('MD5 Password: ')
            privpass = getpass.getpass('AES Password: ')
            if h.is_str_length(username, 1, 'Username') and h.is_str_length(authpass, 8, 'AuthPass') and h.is_str_length(
                    privpass, 8, 'PrivPass'):
                security = cmdgen.UsmUserData(username, authKey=authpass, authProtocol=cmdgen.usmHMACMD5AuthProtocol,
                                              privKey=privpass, privProtocol=cmdgen.usmAesCfb128Protocol)
                return
        elif selection == '6':
            username = input('\nUsername    : ')
            authpass = getpass.getpass('SHA Password: ')
            privpass = getpass.getpass('DES Password: ')
            if h.is_str_length(username, 1, 'Username') and h.is_str_length(authpass, 8, 'AuthPass') and h.is_str_length(
                    privpass, 8, 'PrivPass'):
                security = cmdgen.UsmUserData(username, authKey=authpass, authProtocol=cmdgen.usmHMACSHAAuthProtocol,
                                              privKey=privpass, privProtocol=cmdgen.usmDESPrivProtocol)
                return
        elif selection == '7':
            username = input('\nUsername     : ')
            authpass = getpass.getpass('SHA Password : ')
            privpass = getpass.getpass('3DES Password: ')
            if h.is_str_length(username, 1, 'Username') and h.is_str_length(authpass, 8, 'AuthPass') and h.is_str_length(
                    privpass, 8, 'PrivPass'):
                security = cmdgen.UsmUserData(username, authKey=authpass, authProtocol=cmdgen.usmHMACSHAAuthProtocol,
                                              privKey=privpass, privProtocol=cmdgen.usm3DESEDEPrivProtocol)
                return
        elif selection == '8':
            username = input('\nUsername    : ')
            authpass = getpass.getpass('SHA Password: ')
            privpass = getpass.getpass('AES Password: ')
            if h.is_str_length(username, 1, 'Username') and h.is_str_length(authpass, 8, 'AuthPass') and h.is_str_length(
                    privpass, 8, 'PrivPass'):
                security = cmdgen.UsmUserData(username, authKey=authpass, authProtocol=cmdgen.usmHMACSHAAuthProtocol,
                                              privKey=privpass, privProtocol=cmdgen.usmAesCfb128Protocol)
                return
        elif selection == '0':
            return
    return

def show_menu():
    selection = '1'

    while selection:
        print('\n####################################################')
        print('\nTarget router:', target)
        print('\nSelect operation:')
        print('----------------------------------------------------')
        print('    1. Set target router')
        print('    2. Set SNMP Security')
        print('    3. Walk LI MIBs')
        print('    ------------------------------------------------')
        print('    4. Create and set Mediation Device')
        print('    5. Delete Mediation Device')
        print('    ------------------------------------------------')
        print('    6. Add and activate new LI Stream TAP(s)')
        print('    7. Delete LI Stream TAP')
        print('    ------------------------------------------------')
        print('    8. Show configured TAPs')
        print('    9. Show Intercept Counters')
        print('    ------------------------------------------------')
        print('    0. Exit')

        selection = input('\nSelect option: ')

        if selection == '1':
            set_target()
        elif selection == '2':
            set_snmp_security()
        elif selection == '3':
            walk_mibs()
        elif selection == '4':
            tap2_md()
        elif selection == '5':
            tap2_md_delete()
        elif selection == '6':
            ip_tap()
        elif selection == '7':
            ip_tap_delete()
        elif selection == '8':
            list_taps()
        elif selection == '9':
            show_intercept_counters()
        elif selection == '0':
            exit()

def check_config():
    if target == '0.0.0.0' or security == '':
        print('\nEither "target" or "SNMPv3 credentials not set. Returning to menu.')
        return 0

    return 1

def main():
    show_menu()

##
## This is the boilerplate that calls the main() function
##

if __name__ == '__main__':
    main()

