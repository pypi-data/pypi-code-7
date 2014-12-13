import pygeoip, os
from django import template
from .. import constants

register = template.Library()

@register.inclusion_tag('uecookie9/message.html', takes_context=True)
def uecookie9(context):
    show = False
    request = context['request']    
    closed = request.COOKIES.get('uecookie_closed')
    
    if not closed:
        ip = request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR')
        filename = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources/GeoIP.dat')
        g = pygeoip.GeoIP(filename)
        result = g.country_name_by_addr(ip)
        
        if result in constants.UE_MEMBERS:
            show = True
    
    return {'show' : show}
