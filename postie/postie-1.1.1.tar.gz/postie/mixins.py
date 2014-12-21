import email.mime.text
import email.utils
import logging


logger = logging.getLogger(__name__)


class CurrentDate:
    """A mixin which sets the ``Date`` header to the current date."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["Date"] = email.utils.formatdate()


class Templatable:
    """
    A mixin which provides methods to add text content to emails from
    templates.
    """
    def _attach_template(self, template, context, subtype):
        text = template.render(**context)
        mime = email.mime.text.MIMEText(text, subtype)
        self.attach(mime)
        return mime

    def attach_template_string(self, string, environment, subtype="plain",
                               **context):
        """
        Attach a template to the MIME container by accepting the template
        directly as a string.
        """
        template = environment.from_string(string)
        self._attach_template(template, context, subtype)

    def attach_template(self, template_name_or_list, environment,
                        subtype="plain", **context):
        """
        Attach a template to the MIME container by accepting a template name
        or list which then gets loaded using the environment.
        """
        template = environment.get_or_select_template(template_name_or_list)
        self._attach_template(template, context, subtype)
