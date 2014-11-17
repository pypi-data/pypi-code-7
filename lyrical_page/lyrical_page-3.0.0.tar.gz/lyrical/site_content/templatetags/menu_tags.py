from django import template
from django.conf import settings

from lyrical.site_content.models import SiteMenu

register = template.Library()


@register.inclusion_tag('site_content/tag_nav.html')
def get_menu(code, current='', limit=2, start=0, level=-1, include_ul=True):
    try:
        menu = SiteMenu.objects.get(site__id=settings.SITE_ID, code=code)
    except SiteMenu.DoesNotExist:
        return {}

    return {'current': current, 'menu': menu, 'limit': limit, 'start': start,
            'level': level + 1, 'include_ul': include_ul}
