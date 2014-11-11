from django.views.generic import ListView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.base import View
from django.shortcuts import render_to_response
from django.template import RequestContext
from braces.views import JSONResponseMixin, LoginRequiredMixin

from ftp_deploy.models import Log, Service


class LogView(LoginRequiredMixin, ListView):

    """View for display logs"""

    model = Log
    context_object_name = 'logs'
    template_name = "ftp_deploy/log/log.html"
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super(LogView, self).get_context_data(**kwargs)
        context['service_list'] = Service.objects.all().values('repo_name',
                                                               'pk')
        return context

    def post(self, request, *args, **kwargs):
        logs = self.get_queryset()
        if self.request.POST['services']:
            logs = logs.filter(service__pk=self.request.POST['services'])

        if not int(self.request.POST['status']):
            logs = logs.filter(status=self.request.POST['status'])
        return render_to_response('ftp_deploy/log/list.html', locals(),
                                  context_instance=RequestContext(request))


class LogSkipDeployView(LoginRequiredMixin, JSONResponseMixin,
                        SingleObjectMixin, View):

    """View for skip fail logs"""

    model = Log

    def post(self, request, *args, **kwargs):
        log = self.get_object()
        log.skip = True
        log.save()
        return self.render_json_response({'status': 'success'})
