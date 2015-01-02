#!/usr/bin/env python

# PyTC
#
# A Python wrapper for the TidyClub API.

import urllib
import urllib2
import json

class Club:
    slug = None
    token = None
    client_id = None
    client_secret = None
    
    def __init__(self, slug, client_id, client_secret):
        """
        Initialise a Club instance.
        
        Keyword arguments:
        slug -- the subdomain 'slug' that this club has been assigned by TidyClub.
        client_id -- The OAuth client ID as prescribed by TidyClub.
        client_secret -- the OAuth client secret as prescribed by TidyClub.
        """
        self.slug = slug
        self.client_id = client_id
        self.client_secret = client_secret
    
    # Authorization.
    
    def auth_authcode_get_url(self, redirect_uri):
        """
        Generate and return a URL to initiate the 'Authorization Code' OAuth authorization flow.
        
        One of the many authorization flows offered by the TidyClub API is the Authorization code
        flow. The Authorization Code flow is the most popular authorization flow, and begins with
        the end user opening a special authorization URL.
        
        See the TidyClub API for more information: https://dev.tidyclub.com/api/authentication
        
        redirect_uri -- The redirection URI that you specified when generating your TidyClub API
                        token.
        """
        return self._url("oauth/authorize?") + urllib.urlencode({
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
        })
    
    def auth_authcode_exchange_code(self, code, redirect_uri):
        """
        Take a temporary authorization code and use it to authorize the Club object.
        
        Use this as the second half of the Authorization Code flow.
        
        Keyword arguments:
        code -- the temporary authorization code provided to you, usually by auth_authcode_get_url().
        redirect_uri -- the redirection URI you chose when signing up for the TidyClub API.
        """
        response = self._call("oauth/token", {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
            "code": code,
            "grant_type": "authorization_code"
        }, method = "POST", prefix = "", auth_required = False)

        print "Access token is: %s" % response['data']['access_token']
        self.token = response['data']['access_token']
    
    # Contacts
    
    def get_contacts(self, search_terms = None, group = None, registered = None, limit = 0, offset = 0):
        """
        Get a list of all contacts associated with the club.
        
        Keyword arguments:
        search_terms -- server-side fuzzy searching that will be applied to the list prior to a limit/offset being
                        enforced.
        group -- the ID of a group to constrain the search to, as opposed to all contacts in the club.
        registered -- undocumented in the API, unsure.
        limit -- limit the returned result to this many entires.
        offset -- offset the returned result by this many entries.
        """
        if group:
            path = "groups/%s/contacts"
        else:
            path = "contacts"
        
        data = {
            "limit": limit,
            "offset": offset
        }
        
        if group:
            data['group'] = group
        
        if search_terms:
            data['search_terms'] = search_terms
        
        if registered:
            data['registered'] = registered
        
        resp = self._call(path, data, "GET");
        
        return resp
    
    def _call(self, path, data = {}, method = "GET", prefix = "api/v1/", headers = {}, decode_json = True, auth_required = True):
        if auth_required:
            if self.authenticated:
                headers["Authorization"] = "Bearer %s" % self.token
            else:
                raise PyTCAuthorizationError("Attempted to make an authorized call while not authorized. Please authorize.")
                
        if method == "GET":
            url = self._url(prefix + path, data)
            req = urllib2.Request(url, headers = headers)
        else:
            url = self._url(prefix + path)
            req = urllib2.Request(url, urllib.urlencode(data), headers)
        
        print "Opening..."
        print "\tURL: %s" % url
        print "\tMethod: %s" % method
        print "\tData: %s" % data
        print "\tEncoded data: %s" % urllib.urlencode(data)
        print "\tHeaders: %s" % headers
        
        try:
            resp = urllib2.urlopen(req)
        except urllib2.HTTPError as e:
            if e.code in (401,422):
                error_json = json.loads(e.read())
                print error_json
                raise PyTCUpstreamError(error_json['error'], error_json['error_description'])
            else:
                raise e
        
        if decode_json:
            data = json.loads(resp.read())
        else:
            data = resp.read()
        
        return {
            "data": data,
            "code": resp.getcode()
        }
    
    def _url(self, path, data = None):
        url = "https://%s.tidyclub.com/%s" % (self.slug, path)
        
        if data:
            url += "?" + urllib.urlencode(data)
        
        return url
    
    
    @property
    def authenticated(self):
        return not (self.token == None)

class PyTCError(Exception):
    def __init__(self, error):
        self.error = error
    
    def __str__(self):
        return repr(self.error)

class PyTCUpstreamError(PyTCError):
    def __init__(self, error, error_description):
        self.error = error
        self.error_description = error_description

    def __str__(self):
        return "A TidyClub API error has been encountered: '%s'. %s" % (self.error, self.error_description)

class PyTCAuthorizationError(PyTCError):
    pass