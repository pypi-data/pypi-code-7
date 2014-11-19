# -*- coding: utf-8 -*-
"""View for AjaxSearch"""
from plone.memoize.view import memoize
from Products.Five.browser import BrowserView, pagetemplatefile
from zope.component import queryMultiAdapter
from zope.traversing.browser.absoluteurl import absoluteURL

#plone.mls.listing imports
from plone.mls.core.navigation import ListingBatch
from plone.mls.listing.api import search
 
#local imports
from customer.lascatalinascr_com.vocabularies import PRICE_RENT_VALUES, PRICE_SALE_VALUES

from pprint import pprint as pp


def encode_dict(in_dict):
    out_dict = {}
    for k, v in in_dict.iteritems():
        if isinstance(v, unicode):
            v = v.encode('utf8')
        elif isinstance(v, str):
            # Must be encoded in UTF-8
            v.decode('utf8')
        out_dict[k] = v
    return out_dict

def getMinMax(beds):
    """Set Min&Max value for beds"""
    out_dict = {}
    minBeds = 0
    maxBeds = 0
    
    for v in beds:
        value = int(v)

        if value > 0 and minBeds <1 and maxBeds <1:
            minBeds= value
            maxBeds= value

        if value < minBeds:
            minBeds = value

        if value > maxBeds:
            maxBeds = value

    out_dict['Min'] = minBeds
    out_dict['Max'] = maxBeds

    return out_dict


class ajaxSearch(BrowserView):
    """Deliver search results for ajax calls"""
    index = pagetemplatefile.ViewPageTemplateFile("templates/ajax_template.pt")

    _listings = None
    _batching = None
    _isRental = None
    _isSale   = None
    _isLot    = None
    _limit    = None
    _agency_listings = None


    def __init__(self, context, request):
        super(ajaxSearch, self).__init__(context, request)
        self.context = context
        self.request = request
        self.update()
        
    def __call__(self):
        return self.render()

    def update(self):
        self.portal_state = queryMultiAdapter((self.context, self.request),
                                                name='plone_portal_state')
        self.context_state = queryMultiAdapter((self.context, self.request),
                                               name='plone_context_state')

        self.request.form = encode_dict(self.request.form)
        request_params = self._get_params
        self._get_listings(request_params)

    @property
    def limit(self):
        """get a limit from the request or set 12"""
        if self._limit is not None:
            return self._limit
        return 12

    @property
    def agency_exclusive(self):
        """show only agenty listings?"""
        if self._agency_listings is not None:
            return self._agency_listings
        return True

    def render(self):
        """Prepare view related data.""" 
        return self.index()

    def prepare_search_params(self, data):
        """Prepare search params."""
        params = {}
     
        for item in data:
            raw = data[item]

            # add & set limit param
            if item =='limit':
                try:
                  self._limit = int(raw)
                except Exception, e:
                    pp(e)
            if item =='agency_listings':
                try:
                  self._agency_listings = bool(raw)
                except Exception, e:
                    pp(e)
            

            # map the custom listing types to the mls search
            if item == 'form.widgets.listing_type' and isinstance(raw, (list, tuple, )):
                lt =''

                if 'rental' in raw:
                    lt += 'rl, cl,'
                    self._isRental = True

                if 'sale' in raw:
                    lt += 'rs, cs,' 
                    self._isSale = True

                #land listings
                if 'lot' in raw:
                    lt += 'll'
                    self._isSale = True
                    self._isLot  = True

                elif self._isSale:
                    # also show land listings if only "Sale" is selected
                    lt += 'll'
                    self._isLot  = False


                params['listing_type'] = lt
                #special object types?
                ot =''
                # condo? no problem.
                if 'condo' in raw:
                    ot += 'condominium,'
                # if "home" is set, objecttype is house
                if 'home' in raw:
                    ot += 'house'

                params['object_type']= ot

            #just include pool param if Yes or No is selected (get all otherwise)
            # new feature: disable pool when land listing
            if item == 'form.widgets.pool':
                if raw != '--NOVALUE--' and not self._isLot:
                  params['pool'] = raw

            if item == 'form.widgets.beds' and not self._isLot:
                    rawMinMax = getMinMax(raw)
                    params['beds_min'] = rawMinMax['Min']
                    params['beds_max'] = rawMinMax['Max']

            #reset form.widgets.view_type
            if item == "form.widgets.view_type" and isinstance(raw, (list, tuple, )):
                viewtype = ''

                if "ocean_view" in raw:
                    viewtype += 'ocean_view, '

                if "garden_view" in raw:
                    viewtype += 'garden_view'

                params['view_type'] = viewtype

                if "oceanfront" in raw:
                    params['location_type'] = 'oceanfront'

            # Remove all None-Type values.
            if data[item] is not None or data[item]=='--NOVALUE--':
                value = data[item]
                if isinstance(value, unicode):
                    value = value.encode('utf-8')
                params[item] = value

        #detect min/max price
        MinMax = self._PriceRange(params)
        if MinMax is not None:
        
            params['price_min'] = MinMax.get('min',None)
            if params['price_min'] is not None:
                try:
                    params['price_min'] = int(params['price_min'])
                except Exception, e:
                    """"""
                    params['price_min'] = None

            params['price_max'] = MinMax.get('max',None)
            if params['price_max'] is not None and params['price_max']!= '':
                try:
                    params['price_max'] = int(params['price_max'])

                except Exception, e:
                    """"""
                    params['price_max'] = None
            else:
                params['price_max'] = None
        
        return params

    def _PriceRange(self, params):
        """Determine which Min and Max prices to use"""
        priceRange={}
        priceRange['min']= None
        priceRange['max']= None

        # if its a Rental&Sales Search OR neither one of these:
        # price range is empty
        if (self._isRental and self._isSale) or not(self._isRental or self._isSale):
            return priceRange
        # only rentals: use rental Price ranges
        elif self._isRental:
            range_key = params.get('form.widgets.price_rent', None)

            if range_key is not None:
                range_price = PRICE_RENT_VALUES.get(range_key, None)
            else:
                return priceRange

            if range_price is not None:
                priceRange['min']= range_price.get('min', None)
                priceRange['max']= range_price.get('max', None)
                return priceRange
            else:
                return priceRange

        # only sales: use Sales Price ranges
        elif self._isSale:
            range_key = params.get('form.widgets.price_sale', None)
            range_price = None

            if range_key is not None:
                range_price = PRICE_SALE_VALUES.get(range_key, None)

            if range_price is not None:
                priceRange['min']= range_price.get('min', None)
                priceRange['max']= range_price.get('max', None)
                return priceRange
            else:
                return priceRange;

        else:
            return priceRange


    @property
    def _get_params(self):
        """map MLS search with custom UI"""
        params = self.request.form
        return self.prepare_search_params(params)

    def _get_listings(self, params):
        """Query the recent listings from the MLS."""
        search_params = {
            'limit': self.limit,
            'offset': self.request.get('b_start', 0),
            'lang': self.portal_state.language(),
            'agency_listings': self.agency_exclusive
        }
        search_params.update(params)
    
        results, batching = search(search_params, context=self.context)
        self._listings = results
        self._batching = batching

    @property
    @memoize
    def listings(self):
        """Return listing results."""
        return self._listings

    @memoize
    def view_url(self):
        """Generate view url."""
        if  self.context_state.is_view_template():
            myUrl = absoluteURL(self.context, self.request) + '/'
        else:          
            myUrl = self.context_state.current_base_url()

        #remove @@ params from the url
        mySplit = myUrl.split('@@')
        myUrl = mySplit[0]

        return myUrl


    @property
    def batching(self):
        return ListingBatch(self.listings, self.limit,
                            self.request.get('b_start', 0), orphan=1,
                            batch_data=self._batching)
