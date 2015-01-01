# -*- coding: utf-8 -*-
""" This module will interface with the MiningRigRentals.com API in an attempt to give you easy access to their api.
# Based off of https://github.com/matveyco/cex.io-api-python
# Modified for MiningRigRentals.com purposes
# Get a key from https://www.miningrigrentals.com/account/apikey
# Licensed The MIT License
"""

import hmac
import hashlib
import time
import urllib
import urllib2
import json
import sys

debug = False
__author__ = 'jcwoltz'
__version__ = '0.3.4'


class api:
    """ This class handles the work to talk to MRR's api
    """
    __api_key = ''
    __api_secret = ''
    __nonce_v = ''

    # Init class
    def __init__(self, api_key, api_secret):
        self.__api_key = api_key
        self.__api_secret = api_secret

    #get timestamp as nonce
    def __nonce(self):
        self.__nonce_v = '{:.10f}'.format(time.time() * 1000).split('.')[0]

    #generate signature
    def __signature(self, post_data):
        string = urllib.urlencode(post_data)  #url encode post data
        signature = hmac.new(self.__api_secret, string, digestmod=hashlib.sha1).hexdigest()  #create signature
        if debug:
            print "\n __signature"
            print string
            print signature
            print "\n"
        return signature

    def __post(self, url, param):  #Post Request (Low Level API call)
        params = urllib.urlencode(param)
        sign = self.__signature(param)
        req = urllib2.Request(url, params, {
            'User-agent': 'Mozilla/4.0 (compatible; MRR API Python client; ' + str(sys.platform) + '; ' + str(
                sys.version) + ')', 'x-api-key': self.__api_key, 'x-api-sign': sign})
        page = urllib2.urlopen(req).read()
        return page

    def api_call(self, target, param={}):  # api call (Middle level)
        url = 'https://www.miningrigrentals.com/api/v1/' + target  #generate url
        self.__nonce()
        param.update({'nonce': self.__nonce_v})
        answer = self.__post(url, param)  #Post Request
        return json.loads(answer)  # generate dict and return

    def getbalance(self):
        """
        Get the confirmed and unconfirmed balance form MRR
        :return: return confirmed and unconfirmed balances
        """
        return self.api_call('account', {'method': 'balance'})

    def myrigs(self):
        """
        :return: return list of rigs you own with detail
        """
        return self.api_call('account', {'method': 'myrigs'})

    def myrentals(self):
        """
        :return: return list of rigs you are actively renting
        """
        return self.api_call('account', {'method': 'myrentals'})

    def list_profiles(self):
        """
        :return: returns list of pool profiles configured for your account
        """
        return self.api_call('account', {'method': 'profiles'})

    def rental_detail(self, rental_id):
        """
        :param rental_id: id number of rental
        :return:
        """
        return self.api_call('rental', {'method': 'detail', 'id': str(rental_id)})

    def rent_rig(self, rentalprofile, hours, rig_id):
        """
        :param rig_id: id
        :return: Returns the detail of rig_id
        """
        return self.api_call('rigs', {'method': 'rent', 'profileid': str(rentalprofile), 'length':str(hours), 'id': str(rig_id)})

    def rig_detail(self, rig_id):
        """
        :param rig_id: id
        :return: Returns the detail of rig_id
        """
        return self.api_call('rigs', {'method': 'detail', 'id': str(rig_id)})

    def rig_list(self, min_hash=0, max_hash=0, min_cost=0, max_cost=0, rig_type='scrypt', showoff='no', order=None,
                 orderdir=None, page=None):
        """
        :param min_hash:
        :param max_hash:
        :param min_cost:
        :param max_cost:
        :param rig_type:
        :param showoff:
        :param order: order is one of 'price','hashrate','minhrs','maxhrs','rating','name'
        :param orderdir: orderdir is one of 'asc','desc'
        :return:
        page for more pages
        """
        params = {'method': 'list', 'type': str(rig_type), 'showoff': str(showoff)}
        if (float(min_hash) > 0):
            params.update({'min_hash': str(min_hash)})
        if (float(max_hash) > 0):
            params.update({'max_hash': str(max_hash)})
        if (float(min_cost) > 0):
            params.update({'min_cost': str(min_cost)})
        if (float(max_cost) > 0):
            params.update({'max_cost': str(max_cost)})
        if order is not None:
            params.update({'order': str(order)})
        if orderdir is not None:
            params.update({'orderdir': str(orderdir)})
        if page is not None:
            params.update({'page': str(page)})
        return self.api_call('rigs', params)

    def rig_update(self, rig_id=None, rig_name=None, rig_status=None, hashrate=None, hash_type=None, price=None,
                   min_hours=None, max_hours=None):
        """
        :param rig_id:
        :param rig_name:
        :param rig_status:
        :param hashrate:
        :param hash_type:
        :param price:
        :param min_hours:
        :param max_hours:
        :return:
        """
        if rig_id is not None:
            params = {'method': 'update', 'id': str(rig_id)}
        else:
            return 'Must specify rig ID'
        if rig_name is not None:
            params.update({'name': str(rig_name)})
        if rig_status is not None:
            if str(rig_status).lower() == 'available':
                params.update({'status': 'available'})
            elif str(rig_status).lower() == 'disabled':
                params.update({'status': 'disabled'})
            else:
                return "Unknown rig Status of: " + str(rig_status) + ". Use available or disabled"
        if price is not None:
            params.update({'price': str(price)})
        if min_hours is not None:
            params.update({'min_hours': str(min_hours)})
        if max_hours is not None:
            params.update({'max_hours': str(max_hours)})
        if hashrate is not None:
            params.update({'hashrate': str(hashrate)})
        if hash_type is not None:
            if hashrate is not None:
                params.update({'hash_type': str(hash_type)})
            else:
                return 'Must define hashrate when hash_type is defined'
        return self.api_call('rigs', params)

