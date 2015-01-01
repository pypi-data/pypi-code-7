import json
import urllib2
import ConfigParser
import os
import sys
from optparse import OptionParser
from inspect import currentframe
import mrrapi
import mrrapi.helpers

debug = False
___version___ = '0.0.1'

def lineno():
    cf = currentframe()
    return cf.f_back.f_lineno

def calculateMaxIncomeAlgo(parsedrigs):
    global mhash
    rentalfee = float(0.03)
    outcome = float(0)
    mhash = float(0)

    namelen = 0

    # Pre-process loop to find longest name
    for algo in parsedrigs:
        algorigs = parsedrigs[algo]
        for x in algorigs:
            nametmp = len(parsedrigs[algo][x])
            if nametmp > namelen:
                namelen = nametmp
            #print x, algo, namelen

    layout = "{0:>" + str(namelen) + "}{1:>10}{2:>10}{3:>13}{4:>17}{5:>14}{6:>14}{7:>10}"
    print(layout.format("  Device Name  ", " Type ", " Speed ","Cur hash 30m","Price  ", "Daily income", "Rented? ","RentID"))

    for algo in parsedrigs:
        algorigs = parsedrigs[algo]
        for x in algorigs:
            rig = mapi.rig_detail(x)
            t = rig['data']
            if debug:
                print t
            rigstat = "available"
            curhash = float(0.0)
            rentid = ''
            mhashrate = float(t['hashrate']['advertised'])/(1000000.0)
            mhash += mhashrate
            admhashrate = nicehash(float(t['hashrate']['advertised'])/(1000000.0))
            dailyprice = mhashrate * float(t['price']) * (1.0 - rentalfee)
            curhash = nicehash(round(float(t['hashrate']['30min'])/10**6,3))
            if (str(t['status']) == 'rented'):
                aih = float(t['available_in_hours'])
                rigstat = "R "
                if 0.1 < aih < 10.0:
                    rigstat += " "
                rigstat += str(aih) + " hrs"
                rentid = str(t['rentalid'])
            elif (str(t['status']) == 'unavailable'):
                rigstat = "disabled"
                outcome -= dailyprice

            print(layout.format(str(t['name']),str(t['type']),str(admhashrate),str(curhash),mrrapi.helpers.ff12(float(t['price'])) ,mrrapi.helpers.ff(dailyprice), rigstat,rentid))
            outcome += dailyprice

    return outcome

def nicehash(mhashrate):
    mhunit = "MH"
    if 1000 <= mhashrate < 1000000:
        mhunit = "GH"
        mhashrate = round(float(mhashrate/1000),3)
    elif mhashrate >= 1000000:
        mhunit = "TH"
        mhashrate = round(float(mhashrate/1000000),3)
    elif mhashrate >= 1000000000:
        mhunit = "PH"
        mhashrate = round(float(mhashrate/1000000000),3)
    return (str(mhashrate) + " " + mhunit)

def main():
    global debug, mapi
    parser = OptionParser()
    parser.add_option("-d", "--debug", action="store_true", dest="debug", default=False, help="Show debug output")
    (options, args) = parser.parse_args()

    if options.debug:
        debug = True
        print options
        print mrrapi.helpers.getTerminalSize()

    (mkey, msecret) = mrrapi.helpers.getmrrconfig()
    mapi = mrrapi.api(mkey,msecret)


    myrigs = mapi.myrigs()
    if myrigs['success'] is not True:
        print "Error getting my rig listings"
        if str(myrigs['message']) == 'not authenticated':
            print 'Make sure you fill in your key and secret that you get from https://www.miningrigrentals.com/account/apikey'
    else:
        prigs = mrrapi.helpers.parsemyrigs(myrigs,True)
        #print prigs
        maxi = calculateMaxIncomeAlgo(prigs)
        bal = mapi.getbalance()
        btcv = mrrapi.helpers.getBTCValue()
        print
        print "Max income/day : %s BTC. USD: %s" % (str(round(maxi,8) - 0.002),str(round(btcv*(maxi -0.002),2)))
        print "Current Balance: %s BTC. USD: %s" % (str(bal['data']['confirmed']),str(round(btcv*float(bal['data']['confirmed']),2)))
        print "Pending Balance: %s BTC. USD: %s" % (str(bal['data']['unconfirmed']),str(round(btcv*float(bal['data']['unconfirmed']),2)))


if __name__ == '__main__':
    main()