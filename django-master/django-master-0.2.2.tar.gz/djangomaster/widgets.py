from django.template.loader import render_to_string


class MasterWidget(object):
    title = 'Master Widget'
    template_name = 'djangomaster/sbadmin/widget/base.html'
    page = 'djangomaster.home'
    _error_template = 'djangomaster/sbadmin/widget/error.html'

    def get_title(self):
        return self.title

    def get_context_data(self):
        return {
            'title': self.get_title()
        }

    def render(self):
        context = self.get_context_data()
        if 'error' in context:
            return render_to_string(self._error_template, context)
        html = render_to_string(self.template_name, context)
        return html
