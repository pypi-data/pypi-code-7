import json
import urllib2
import mrrapi
import ConfigParser
import os
import sys
from optparse import OptionParser
from inspect import currentframe

debug = False
config = ConfigParser.ConfigParser()

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

def getTerminalSize():
    import os
    env = os.environ
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
        '1234'))
        except:
            return
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

        ### Use get(key[, default]) instead of a try/catch
        #try:
        #    cr = (env['LINES'], env['COLUMNS'])
        #except:
        #    cr = (25, 80)
    return int(cr[1]), int(cr[0])

mapi = mrrapi.api(mkey,msecret)
debug = False
#helper function to format floats
def ff(f):
    return format(f, '.8f')

#helper function to format floats
def ff12(f):
    return format(f, '.12f')


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
    global debug
    parser = OptionParser()
    parser.add_option("-d", "--debug", action="store_true", dest="debug", default=False, help="Show debug output")
    (options, args) = parser.parse_args()

    if options.debug:
        debug = True
        print options
        print getTerminalSize()

    myrigs = mapi.myrigs()
    if myrigs['success'] is not True:
        print "Error getting my rig listings"
        if str(myrigs['message']) == 'not authenticated':
            print 'Make sure you fill in your key and secret that you get from https://www.miningrigrentals.com/account/apikey'
    else:
        prigs = parsemyrigs(myrigs,True)
        #print prigs
        maxi = calculateMaxIncomeAlgo(prigs)
        bal = mapi.getbalance()
        btcv = getBTCValue()
        print
        print "Max income/day : %s BTC. USD: %s" % (str(round(maxi,8) - 0.002),str(round(btcv*(maxi -0.002),2)))
        print "Current Balance: %s BTC. USD: %s" % (str(bal['data']['confirmed']),str(round(btcv*float(bal['data']['confirmed']),2)))
        print "Pending Balance: %s BTC. USD: %s" % (str(bal['data']['unconfirmed']),str(round(btcv*float(bal['data']['unconfirmed']),2)))


if __name__ == '__main__':
    main()