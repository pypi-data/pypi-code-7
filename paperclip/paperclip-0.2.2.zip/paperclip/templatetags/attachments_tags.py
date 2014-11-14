import mimetypes

from django.template import Library, Node, Variable
from django.utils.translation import ugettext_lazy as _

from paperclip.forms import AttachmentForm
from paperclip.models import Attachment


register = Library()


@register.filter
def icon_name(value):
    mimetype = value.mimetype
    if not mimetype or mimetype == ('application', 'octet-stream'):
        return 'bin'
    ext = mimetypes.guess_extension('/'.join(mimetype))
    return ext[1:] if ext else 'bin'


@register.inclusion_tag('paperclip/_attachment_form.html', takes_context=True)
def attachment_form(context, obj, form=None):
    """
    Renders a "upload attachment" form.
    """
    # Unbound form by default (this is why a template tag is used!)
    if form is None:
        request = context['request']
        next_url = context['attachment_form_next']
        form = AttachmentForm(request, object=obj, next_url=next_url)

    form_title = _("New file attachment")
    if form.instance.pk:
        form_title = u"%s %s" % (_("Update"), form.instance.filename)

    return {
        'attachment_form': form,
        'form_title': form_title,
    }


class AttachmentsForObjectNode(Node):
    def __init__(self, obj, var_name):
        self.obj = obj
        self.var_name = var_name

    def resolve(self, var, context):
        """Resolves a variable out of context if it's not in quotes"""
        if var[0] in ('"', "'") and var[-1] == var[0]:
            return var[1:-1]
        else:
            return Variable(var).resolve(context)

    def render(self, context):
        obj = self.resolve(self.obj, context)
        var_name = self.resolve(self.var_name, context)
        context[var_name] = Attachment.objects.attachments_for_object(obj)
        return ''


@register.tag
def get_attachments_for(parser, token):
    """
    Resolves attachments that are attached to a given object. You can specify
    the variable name in the context the attachments are stored using the `as`
    argument. Default context variable name is `attachments`.

    Syntax::

        {% get_attachments_for obj %}
        {% for att in attachments %}
            {{ att }}
        {% endfor %}

        {% get_attachments_for obj as "my_attachments" %}

    """
    def next_bit_for(bits, key, if_none=None):
        try:
            return bits[bits.index(key)+1]
        except ValueError:
            return if_none

    bits = token.contents.split()
    args = {
        'obj': next_bit_for(bits, 'get_attachments_for'),
        'var_name': next_bit_for(bits, 'as', '"attachments"'),
    }
    return AttachmentsForObjectNode(**args)
