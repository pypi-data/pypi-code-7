from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic.detail import View

from djangomaster.sites import mastersite
from djangomaster.conf import settings as mastersettings


class MasterView(View):
    name = 'base'
    label = 'Django Master'
    title = 'Django Master'
    template_name = 'djangomaster/base.html'
    widgets = ()

    def get_title(self):
        return self.title

    def get_widgets(self):
        return self.widgets

    def get_menu(self):
        return mastersite.get_menu()

    def get_footer(self):
        return ''

    def get_context_data(self, **kwargs):
        item_name = getattr(self, 'slug', '')

        context = {
            'title': self.get_title(),
            'widgets': self.get_widgets(),
            'mastermenu': self.get_menu(),
            'mastermenu_module': item_name.split('-')[0],
            'mastermenu_item': item_name,
            'footer': self.get_footer(),
            'params': kwargs,
            'settings': mastersettings,
        }

        return context

    def render_to_response(self, context):
        return render(self.request, self.template_name, context)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied

        return super(MasterView, self).dispatch(request, *args, **kwargs)


# class JSONResponseMixin(object):
#     """
#     # @see https://docs.djangoproject.com/en/1.4/topics/class-based-views/
#     """

#     def render_to_response(self, context):
#         "Returns a JSON response containing 'context' as payload"
#         return self.get_json_response(self.convert_context_to_json(context))

#     def get_json_response(self, content, **httpresponse_kwargs):
#         "Construct an `HttpResponse` object."
#         return HttpResponse(content, content_type='application/json',
#                             **httpresponse_kwargs)

#     def convert_context_to_json(self, context):
#         "Convert the context dictionary into a JSON object"
#         # Note: This is *EXTREMELY* naive; in reality, you'll need
#         # to do much more complex handling to ensure that arbitrary
#         # objects -- such as Django model instances or querysets
#         # -- can be serialized as JSON.

#         if 'object' in context:
#             return json.dumps(context['object'], cls=DjangoJSONEncoder)
#         else:
#             return json.dumps(context, cls=DjangoJSONEncoder)


# class JSONDetailView(JSONResponseMixin, BaseDetailView):
#     pass


# class MasterJSONView(JSONResponseMixin, ListView):
#     @method_decorator(login_required)
#     def dispach(self, *args, **kwargs):
#         if not self.request.user.is_admin:
#             raise PermissionDenied

#         return super(JSONDetailView, self).dispach(*args, **kwargs)
