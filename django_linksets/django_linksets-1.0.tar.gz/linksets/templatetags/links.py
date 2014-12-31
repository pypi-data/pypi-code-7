from django.template import Library

from ..models import LinkItem

register = Library()


@register.assignment_tag()
def get_link_descendants(txtid):
    """
    This tag gets the children and (if they're there) grandchildren of a link item.
    """

    output = []
    try:
        children = LinkItem.objects.filter(parent__txtid=txtid)\
            .exclude(hide=True).order_by('order')
        for child in children:
            output.append({
                'item':child,
                'children':get_link_descendants(child.txtid)
            })
    except:
        return None

    return output
