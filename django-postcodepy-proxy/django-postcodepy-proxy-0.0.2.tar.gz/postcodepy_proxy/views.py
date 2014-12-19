"""
Provides an PostcodepyProxyView class that 
"""

from django.views.generic  import View

from django.conf import settings
from postcodepy import postcodepy

USER_SETTINGS = getattr(settings, "POSTCODEPY", None)

class PostcodepyProxyView(View):
  def get(self, request, *args, **kwargs):

   api = postcodepy.API( environment='live', access_key=USER_SETTINGS['AUTH']['API_ACCESS_KEY'], access_secret=USER_SETTINGS['AUTH']['API_ACCESS_SECRET'])
   pcat = ( kwargs['postcode'], kwargs['houseNumber'], kwargs['houseNumberAddition'] if kwargs.has_key('houseNumberAddition') else "" )

   retValue = api.get_postcodedata( *pcat )
   return retValue

class SignalProxyView(View):
  def get(self, request, sar, *args, **kwargs):

   api = postcodepy.API( environment='live', access_key=USER_SETTINGS['AUTH']['API_ACCESS_KEY'], access_secret=USER_SETTINGS['AUTH']['API_ACCESS_SECRET'])
   retValue = api.get_signalcheck( sar )
   return retValue

