#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
import urllib2
import mrrapi
import ConfigParser
import os
import sys
from datetime import datetime, timedelta
import requests
from optparse import OptionParser
from inspect import currentframe
from pytz import timezone

debug = False
config = ConfigParser.ConfigParser()
PoolPickerIgnore = ['AltMining.Farm', 'MagicPool']
ppa = 1.1  # When rig is available, add 25% above max poolpicker payout
ppr = 1.1  #    When rig is rented, add 35% above max poolpicker payout
mrrrigs = {}
mrrprices = []

for loc in os.curdir, os.path.expanduser("~"), os.path.expanduser("~/.mrrapi"), os.path.expanduser("~/mrrapi"):
    try:
        with open(os.path.join(loc,"mrrapi.cfg")) as source:
            config.readfp(source)
            if debug:
                print "DEBUG: Using %s for config file" % (str(source.name))
    except IOError:
        pass

mkey = config.get('MRRAPIKeys','key')
msecret = config.get('MRRAPIKeys','secret')

def lineno():
    cf = currentframe()
    return cf.f_back.f_lineno

mapi = mrrapi.api(mkey,msecret)
reload(sys)
sys.setdefaultencoding('utf-8')
#helper function to format floats
def ff(f):
    return format(f, '.8f')

#helper function to format floats
def ff12(f):
    return format(f, '.12f')

def getPoolPickerAlgo(algo='ScryptN'):
    global algobtc, poolbtc
    algobtc = []
    poolbtc = {}
    dfmt = '%Y-%m-%d'
    nowTime = datetime.now(timezone('EST5EDT')).strftime(dfmt)
    yDate = (datetime.now() - timedelta(days=1)).strftime(dfmt)
    if debug:
        print " Looking for Date: " + nowTime
    layout = "{0:>45}{1:>20}"
    url = "http://poolpicker.eu/api"
    res = requests.get(url, verify=False)
    if (requests.__version__.split('.')[0] > 0):  #Detect old version of requests used by distros
        tr = res.json()
    else:
        tr = res.json
    if verbose:
        print(layout.format(" Pool Name ", "Payout "))
    for x in tr['pools']:
        if x['profitability'].has_key(algo):  # Make sure this pool has selected algo
            if x['profitability'][algo][0]['date'] == nowTime or x['profitability'][algo][0]['date'] == yDate:  # Look at today only
                if str(x['name']) not in PoolPickerIgnore:  # pools to ignore
                    if str(algo) == 'SHA256':  # PP reports sha256 in THs
                        algobtc.append(float(x['profitability'][algo][0]['btc']) / 10 ** 6)  #bring TH down to MH
                        poolbtc[str(x['name'])] = float(x['profitability'][algo][0]['btc']) / 10 ** 6
                        if verbose:
                            print(layout.format(str(x['name']),
                                                str(round(float(x['profitability'][algo][0]['btc']) / 10 ** 6, 12))))
                    elif str(algo) == 'Keccak':
                        algobtc.append(float(x['profitability'][algo][0]['btc']) / 10 ** 3)  #bring GH down to MH
                        poolbtc[str(x['name'])] = float(x['profitability'][algo][0]['btc']) / 10 ** 3
                        if verbose:
                            print(layout.format(str(x['name']),
                                                str(round(float(x['profitability'][algo][0]['btc']) / 10 ** 3, 12))))
                    else:
                        algobtc.append(float(x['profitability'][algo][0]['btc']))
                        poolbtc[str(x['name'])] = float(x['profitability'][algo][0]['btc'])
                        if verbose:
                            print(
                            layout.format(str(x['name']), str(round(float(x['profitability'][algo][0]['btc']), 10))))
            else:
                if debug:
                    print "Ignoring pool " + str(x['name']) + " due to a past date of " + str(
                        x['profitability'][algo][0]['date'])
    if verbose:
        print(layout.format(" ---------------", "  ----------"))
    if len(algobtc) > 0:
        algobtc.sort()
        if verbose:
            print(layout.format(" Max Payout", round(max(algobtc), 8)))
        if debug:
            print algobtc
            print poolbtc
        return max(algobtc)
    else:
        print "No Pricing available"
        return 1


def getmrrlow(ignoreFirstrigs=0, min_price=0):
    global mrrrigs, mrrprices
    mrrpp = []
    # Get a list of rigs above 10MHs and above min_price of rig_type
    mrrp = mapi.rig_list(10, 0, min_price, rig_type=mrralgo)
    if (str(mrrp['success'] == 'True') and len(mrrp['data']['records']) > 0):  #make sure we have valid data
        for x in mrrp['data']['records']:
            if int(x['id']) not in mrrdevices:  #make sure it is not my rig
                if debug:
                    print x
                if str(x['status']).lower() == 'available':  #only compare available rigs
                    if float(x['rating']) > 4.0:  #only compare highly rated rigs
                        mrrrigs.update({int(x['id']): {'hashrate': float(x['hashrate']), 'price': float(x['price'])}})
                        mrrpp.append(float(x['price']))
                    elif debug:
                        print "Ignoring rig: " + str(x['id']) + " With a rating of " + str(x['rating']) + " for " + str(
                            x['name'])
        for e in mrrpp:
            if e not in mrrprices:
                mrrprices.append(e)
        mrrprices.sort()
        if len(mrrprices) > ignoreFirstrigs:
            if debug:
                print mrrprices[ignoreFirstrigs - 1]
            return mrrprices[ignoreFirstrigs - 1]
        elif len(mrrprices) > 0:
            print "WARNING: " + str(len(mrrprices)) + " prices instead of " + str(ignoreFirstrigs) + " asked for. "
            ignoreFirstrigs = len(mrrprices) - 1
            if debug:
                print mrrprices[ignoreFirstrigs]
            return mrrprices[ignoreFirstrigs]
        else:
            print "Problem with pricing length"
            return 1
    else:
        print "MRR Data failure or no rigs in specs"
        return 1


def setRigPrice(rigId, setPrice, rigDetail=None):
    if rigDetail is not None:
        if float(rigDetail['data']['price']) != float(setPrice):
            if verbose:
                print "Changing rig " + str(rigDetail['data']['id']) + " price from: " + str(
                    float(rigDetail['data']['price'])) + " to " + str(setPrice)
            mapi.rig_update(str(rigDetail['data']['id']), price=str(setPrice))
        else:
            if verbose:
                print "Rig " + str(rigDetail['data']['id']) + " already at " + str(setPrice)
    else:
        if verbose:
            print "Setting Rig " + str(rigId) + " price: " + str(setPrice)
        mapi.rig_update(str(rigId), price=str(setPrice))


def updatemyRigsPrices(percenta, percentr, setPrice, ppPrice):
    """
    :param percenta: Multiplier for max PoolPicker Price when rig available
    :param percentr: Multiplier for max PoolPicker Price when rig is rented
    :param setPrice: Lowest setPrice to set rig. Lowest rate you will accept
    :param ppPrice: Price from poolpicker or other function. this will be multiplied by percent a and r
    :return:
    """
    for x in mrrdevices:
        t = mapi.rig_detail(x)
        if debug:
            print t
        if str(t['data']['status']) == 'available':
            if setPrice > (ppPrice * percenta):
                setRigPrice(x, setPrice, t)
            else:
                setRigPrice(x, (ppPrice * percenta), t)
        elif str(t['data']['status']) == 'rented':
            if setPrice > (ppPrice * percentr):
                setRigPrice(x, setPrice, t)
            else:
                setRigPrice(x, (ppPrice * percentr), t)
        else:
            if setPrice > (ppPrice * percentr):
                setRigPrice(x, setPrice, t)
            else:
                setRigPrice(x, (ppPrice * percentr), t)


def calculateMaxIncomeA():
    global outcome, mhash
    rentalfee = float(0.035)
    outcome = float(0)
    mhash = float(0)
    layout = "{0:>65}{1:>10}{2:>10}{3:>15}{4:>14}"
    print(layout.format("  Device Name  ", " Speed ", "Price  ", "Daily income", "Rented? "))
    for x in mrrdevices:
        t = mapi.rig_detail(x)
        rigstat = "available"
        if (t['success'] == True):
            mhashrate = float(float(t['data']['hashrate']['advertised']) / (1000000.0))
            mhash += mhashrate
            dailyprice = mhashrate * float(t['data']['price']) * (1.0 - rentalfee)
            if (str(t['data']['status']) == 'rented'):
                aih = float(t['data']['available_in_hours'])
                rigstat = "R "
                if 0.1 < aih < 10.0:
                    rigstat += " "
                rigstat += str(aih) + " hrs"
            elif (str(t['data']['status']) == 'unavailable'):
                rigstat = "disabled"
            print(
            layout.format(str(t['data']['name']), str(mhashrate) + " MH", str(round(float(t['data']['price']), 6)),
                          str(round(dailyprice, 8)), rigstat))
            outcome += dailyprice
        if debug:
            print t


def printCalcs():
    btc_usd = getBTCValue()

    #get the max payout from poolpicker
    ppmax = getPoolPickerAlgo(ppalgo)
    # you can replace getPoolPicker with your own function that returns the highest paying pool price

    # the getmrrlow takes 2 arguments
    #  number of lowest prices to ignore
    #  poolpicker max payout
    mrrlow = getmrrlow(3, ppmax)

    #print "PoolPicker Max: " + str(ppmax)
    print "MRR Lowest    : " + str(mrrlow)
    #The following command triggers all of the work.
    # There are four main argument to updateMyRigsPrices
    #  ppa is set at top of file
    #  ppr is set at top of file
    #  Lowest price we will set
    #  Highest payout on poolpicker
    updatemyRigsPrices(ppa, ppr, mrrlow, ppmax)

    calculateMaxIncomeA()
    mrrdaily = outcome - 0.0002

    print "Total Hashing power: " + str(mhash)
    print "MRR BTC: " + str(mrrdaily) + " USD: " + str(mrrdaily * btc_usd)
    #print "Max weekly perfect conditions: ",
    #print (outcome - 0.0002) * btc_usd * 7
    #print "Likely weekly rentals (90%): " + str((0.9 * outcome - 0.0002) * btc_usd * 7)
    #print "CM Weekly: " + str(cmdaily * btc_usd * 7)

def printMCalcs(setPrice):
    btc_usd = getBTCValue()
    updatemyRigsPrices(1, 1, setPrice, setPrice)

    calculateMaxIncomeA()
    mrrdaily = outcome - 0.0002

    print "Total Hashing power: " + str(mhash)
    print "MRR BTC: " + str(mrrdaily) + " USD: " + str(mrrdaily * btc_usd)

def getriginfo(rigid):
    #this maps the mrr algo to the poolpicker algo
    algomap = {'sha256': 'SHA256', 'scrypt': 'Scrypt', 'scryptn': 'ScryptN', 'x11': 'X11', 'x13': 'X13', 'x15': 'X15'}
    global rig, ppalgo, mrralgo, mrrdevices
    try:
        rid = int(rigid)
    except:
        return "Must use a number"
    try:
        rig = mapi.rig_detail(rid)
        print rig
        rigtype = rig['data']['type']
        if algomap.has_key(str(rigtype)):
            ppalgo = algomap[str(rigtype)]
            mrrdevices = [rid]
            mrralgo = str(rigtype)
        else:
            print "Unknown algo mapping for %s" % (str(rigtype))
            return "Unknown Algo"
    except:
        return "Connection Error"








def getBTCValue():
    # https://www.bitstamp.net/api/  BTC -> USD
    bitstampurl = "https://www.bitstamp.net/api/ticker/"
    try:
        bsjson = urllib2.urlopen(bitstampurl).read()
        dbstamp_params = json.loads(bsjson)
        btc_usd = float(dbstamp_params['last'])
    except:
        print "Unable to retrieve BTC Value"
        btc_usd = float(1.1)
    return btc_usd

def parsemyrigs(rigs,list_disabled=False):
    """
    :param rigs: pass the raw api return from mrrapi.myrigs()
    :param list_disabled: Boolean to list the disabled rigs
    :return: returns dict by algorithm
    """
    global mrrrigs
    mrrrigs = {}
    # I am not a python programmer, do you know a better way to do this?
    # first loop to create algo keys
    # second loop populates rigs in algo
    for x in rigs['data']['records']:
        mrrrigs.update({str(x['type']): {}})
    for x in rigs['data']['records']:
        if debug:
            print x
        if (list_disabled or str(x['status']) != 'disabled') and not (str(x['name']).__contains__('retired') or str(x['name']).__contains__('test')):
            mrrrigs[str(x['type'])][int(x['id'])] = str(x['name'])
    if debug:
        print mrrrigs
    return mrrrigs

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

            print(layout.format(str(t['name']),str(t['type']),str(admhashrate),str(curhash),ff12(float(t['price'])) ,ff(dailyprice), rigstat,rentid))
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
    global debug, verbose
    verbose=False
    parser = OptionParser()
    parser.add_option("-d", "--debug", action="store_true", dest="debug", default=False, help="Show debug output")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Show verbose output")
    parser.add_option("-r", "--rigid", action="store", dest="rigid", help="RigID of rig to set price of", type="long")
    parser.add_option("-p", "--price", action="store", dest="rigprice", help="Price to set of RigID", type="float")
    parser.add_option("-c", "--calculated", action="store_true", dest="calculated", default=False, help="Automatically calculate price based off of payouts")
    (options, args) = parser.parse_args()

    if options.debug:
        debug = True
        print options
    if options.verbose:
        verbose = True
        print options
    if options.rigid is None or (options.rigprice is None and options.calculated is False):
        if options.rigid is None:
            print "ERROR: You must define a rig id to update."
        if (options.rigprice is None and options.calculated is False):
            print "ERROR: You must define a price or use the calculated option"
        sys.exit(1)

    print getriginfo(str(options.rigid))
    if options.calculated:
        printCalcs()
        sys.exit(0)
    elif options.rigprice:
        printMCalcs(options.rigprice)
        sys.exit(0)

    sys.exit(2)

    #myrigs = mapi.myrigs()
    #if myrigs['success'] is not True:
    #    print "Error getting my rig listings"
    #    if str(myrigs['message']) == 'not authenticated':
    #        print 'Make sure you fill in your key and secret that you get from https://www.miningrigrentals.com/account/apikey'
    #else:
    #    prigs = parsemyrigs(myrigs,True)
    #    #print prigs
    #    maxi = calculateMaxIncomeAlgo(prigs)
    #    bal = mapi.getbalance()
    #    btcv = getBTCValue()
    #    print
    #    print "Max income/day : %s BTC. USD: %s" % (str(round(maxi,8) - 0.002),str(round(btcv*(maxi -0.002),2)))
    #    print "Current Balance: %s BTC. USD: %s" % (str(bal['data']['confirmed']),str(round(btcv*float(bal['data']['confirmed']),2)))
    #    print "Pending Balance: %s BTC. USD: %s" % (str(bal['data']['unconfirmed']),str(round(btcv*float(bal['data']['unconfirmed']),2)))


if __name__ == '__main__':
    main()