import json

from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import (ListView, UpdateView, DeleteView,
                                  DetailView, CreateView)
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect, Http404

from braces.views import JSONResponseMixin, LoginRequiredMixin

from ftp_deploy.conf import *
from ftp_deploy.models import Service
from ftp_deploy.utils.repo import commits_parser
from ftp_deploy.server.forms import ServiceForm, ServiceNotificationForm


class DashboardView(LoginRequiredMixin, ListView):

    """View for dashboard"""

    model = Service
    queryset = Service.objects.all().select_related().order_by(
        "status", "-log__created").annotate(date=Max('log__created'))
    context_object_name = 'services'
    template_name = "ftp_deploy/dashboard.html"
    paginate_by = 25

    def post(self, request, *args, **kwargs):
        services = self.get_queryset()
        if self.request.POST['services']:
            services = services.filter(pk=self.request.POST['services'])
        return render_to_response('ftp_deploy/service/list.html', locals(),
                                  context_instance=RequestContext(request))


class ServiceManageView(LoginRequiredMixin, DetailView):

    """View for manage services"""

    model = Service
    context_object_name = 'service'
    template_name = "ftp_deploy/service/manage.html"

    def get_context_data(self, **kwargs):
        context = super(ServiceManageView, self).get_context_data(**kwargs)
        context['recent_logs'] = self.object.log_set.all()[:15]
        context['fail_logs'] = self.object.log_set.filter(
            status=0).filter(skip=0)
        return context


class ServiceAddView(LoginRequiredMixin, CreateView):

    """View for add serives"""
    model = Service
    form_class = ServiceForm
    template_name = "ftp_deploy/service/form.html"

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS,
                             'Service has been added.')
        return super(ServiceAddView, self).form_valid(form)

    def get_success_url(self):
        self.object.validate()
        self.object.save()
        return reverse('ftpdeploy_service_manage',
                       kwargs={'pk': self.object.pk})


class ServiceEditView(LoginRequiredMixin, UpdateView):

    """View for edit services"""
    model = Service
    form_class = ServiceForm
    template_name = "ftp_deploy/service/form.html"

    def form_valid(self, form):
        self.object.validate()
        self.object.save()
        messages.add_message(self.request, messages.SUCCESS,
                             'Service has been updated.')
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('ftpdeploy_service_manage',
                       kwargs={'pk': self.kwargs['pk']})


class ServiceDeleteView(LoginRequiredMixin, DeleteView):

    """View for delete services"""

    model = Service
    success_url = reverse_lazy('ftpdeploy_dashboard')
    template_name = "ftp_deploy/service/delete.html"

    def delete(self, request, *args, **kwargs):
        messages.add_message(request, messages.SUCCESS,
                             'Service has been removed.')
        return super(ServiceDeleteView, self).delete(request, *args, **kwargs)


class ServiceStatusView(JSONResponseMixin, LoginRequiredMixin,
                        SingleObjectMixin, View):

    """View for update(save) and check service status"""

    model = Service

    def post(self, request, *args, **kwargs):
        service = self.get_object()
        service.validate()
        service.save()
        response = request.POST.get('response', '')

        if response == 'list':
            services = [service]
            return render_to_response('ftp_deploy/service/list.html', locals(),
                                      context_instance=RequestContext(request))

        if response == 'manage':
            manage_view = ServiceManageView()
            manage_view.object = service
            context = manage_view.get_context_data()
            return render_to_response(
                'ftp_deploy/service/manage.html',
                context, context_instance=RequestContext(request))

        if response == 'json':
            context = {
                'status': service.status,
                'status_message': service.status_message,
                'updated': service.updated
            }
            return self.render_json_response(context)

        raise Http404


class ServiceRestoreView(LoginRequiredMixin, DetailView):

    """"View for build restore path for service"""

    model = Service
    prefetch_related = ["log_set"]
    template_name = "ftp_deploy/service/restore-modal.html"

    def get_context_data(self, **kwargs):
        context = super(ServiceRestoreView, self).get_context_data(**kwargs)

        service = self.get_object()
        logs = service.get_logs_tree()

        # init payload dictionary
        context['payload'] = json.loads(logs[0].payload)

        if service.repo_source == 'bb':
            context['payload']['user'] = 'Restore'
        elif service.repo_source == 'gh':
            context['payload']['pusher']['name'] = 'Restore'

        context['service'] = service

        commits = list()
        for log in logs:
            payload = json.loads(log.payload)
            commits += payload['commits']

        context['payload']['commits'] = commits
        context['payload'] = json.dumps(context['payload'])

        context['files_added'], context['files_modified'], context['files_removed'] = commits_parser(commits, service.repo_source).file_diff()
        context['commits_info'] = commits_parser(commits, service.repo_source).commits_info()

        return context

    def post(self, request, *args, **kwargs):
        if self.get_object().lock():
            return HttpResponse(status=500)

        return HttpResponse(
            reverse('ftpdeploy_deploy',
                    kwargs={'secret_key': self.get_object().secret_key}))


class ServiceNotificationView(LoginRequiredMixin, UpdateView):

    model = Service
    form_class = ServiceNotificationForm
    template_name = "ftp_deploy/notification/notification-modal.html"

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS,
                             'Service notification has been updated.')
        return super(ServiceNotificationView, self).form_valid(form)

    def get_success_url(self):
        return reverse('ftpdeploy_service_manage',
                       kwargs={'pk': self.kwargs['pk']})
