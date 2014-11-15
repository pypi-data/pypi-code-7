from django import template
from django.utils import translation
from tinycms.models import *
from tinycms_menu.models import *

register = template.Library()

def internal_create_children_menu(item,sublevel,lang,tag):
    result =""
    menus = MenuItem.objects.filter(page=item,language=lang)
    if(menus.count()!=0):
        result = result + "<li><a href='"+item.get_absolute_url()+"'>"+menus[0].title+"</a>"
        if(sublevel>0):
            if(item.get_children().count()>0):
                result = result +"<"+tag+">"+ create_children_menu(item,sublevel-1,lang,tag) +"</"+tag+">"
        result = result+"</li>"
    return result


def create_children_menu(parent,sublevel,lang,tag):
    result =""
    for item in parent.get_children():
        result = result + internal_create_children_menu(item,sublevel,lang,tag)
    return result


@register.simple_tag(takes_context=True)
def show_absolute_menu(context, sublevel = 0, tag="ul"):
    """Show absolute menu.

    """
    page_roots = Page.objects.root_nodes()
    result =""

    lang = translation.get_language()

    for item in page_roots:
        result = result + internal_create_children_menu(item,sublevel,lang,tag)
    return result


@register.simple_tag(takes_context=True)
def show_submenu(context, sublevel = 0,showSiblings=False, tag="ul"):
    """Show sub menu.

    """
    current = context["page"]

    lang = translation.get_language()

    result = ""

    if(showSiblings):
        siblings = current.get_siblings(include_self=True)
        for item in siblings:
            if(item!=current):
                result = result + internal_create_children_menu(item,0,lang,tag)
            else:
                result = result + internal_create_children_menu(item,sublevel,lang,tag)
    else:
        result = internal_create_children_menu(current,sublevel,lang,tag)
    return result


