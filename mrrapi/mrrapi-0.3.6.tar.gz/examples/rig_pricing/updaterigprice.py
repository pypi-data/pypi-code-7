#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import json
import urllib2
from datetime import datetime, timedelta
import requests
from pytz import timezone

import mrrapi
# #############################################################################
##############################################################################
# Change settings here
# Verbose displays useful info. Turn off if you do not want it displayed
verbose = True
# Turn debug on to see all info
debug = False

# your key and secret
mkey = 'YourKey'
msecret = 'YourSecret'

ppa = 1.25  # When rig is available, add 25% above max poolpicker payout
ppr = 1.35  #    When rig is rented, add 35% above max poolpicker payout
# Pools to ignore from poolpicker
PoolPickerIgnore = ['AltMining.Farm', 'bobpool']
##############################################################################
##############################################################################
##############################################################################
try:
    from jckey import mkey, msecret
except:
    pass

mapi = mrrapi.api(mkey, msecret)
reload(sys)
sys.setdefaultencoding('utf-8')

mrrrigs = {}
mrrprices = []


def getBTCValue():
    # https://www.bitstamp.net/api/  BTC -> USD
    bitstampurl = "https://www.bitstamp.net/api/ticker/"
    bsjson = urllib2.urlopen(bitstampurl).read()
    dbstamp_params = json.loads(bsjson)
    btc_usd = float(dbstamp_params['last'])
    return btc_usd


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


if __name__ == '__main__':
    arglen = len(sys.argv)
    cmdargs = str(sys.argv)
    #print ("The total numbers of args passed to the script: %d " % arglen)
    #print ("Args list: %s " % cmdargs)
    if arglen < 2:
        print 'USAGE: %s rigid' % ('updaterigprice.py')
    else:
        print getriginfo(str(sys.argv[1]))
        printCalcs()
        #read through printCalcs for explanation and where else to read