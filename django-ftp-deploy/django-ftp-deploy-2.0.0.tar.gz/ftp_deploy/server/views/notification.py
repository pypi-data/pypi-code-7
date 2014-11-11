from django.views.generic import ListView, UpdateView, DeleteView, CreateView
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages

from braces.views import LoginRequiredMixin

from ftp_deploy.models import Notification
from ftp_deploy.server.forms import NotificationForm


class NotificationView(LoginRequiredMixin, ListView):

    model = Notification
    template_name = 'ftp_deploy/notification/notification.html'
    context_object_name = 'notifications'


class NotificationAddView(LoginRequiredMixin, CreateView):

    """View for add notifications"""

    model = Notification
    form_class = NotificationForm
    success_url = reverse_lazy('ftpdeploy_notification')
    template_name = "ftp_deploy/notification/form.html"

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS,
                             'Notification has been added.')
        return super(NotificationAddView, self).form_valid(form)


class NotificationEditView(LoginRequiredMixin, UpdateView):

    """View for edit notifications"""

    model = Notification
    form_class = NotificationForm
    success_url = reverse_lazy('ftpdeploy_notification')
    template_name = "ftp_deploy/notification/form.html"

    def get_context_data(self, **kwargs):
        context = super(NotificationEditView, self).get_context_data(**kwargs)
        emails = self.get_object().get_email_list()
        context['emails'] = emails
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS,
                             'Notification has been updated.')
        return super(NotificationEditView, self).form_valid(form)


class NotificationDeleteView(LoginRequiredMixin, DeleteView):

    """View for delete services"""

    model = Notification
    success_url = reverse_lazy('ftpdeploy_notification')
    template_name = "ftp_deploy/notification/delete.html"

    def delete(self, request, *args, **kwargs):
        messages.add_message(request, messages.SUCCESS,
                             'Notification has been removed.')
        return super(NotificationDeleteView, self).delete(request, *args,
                                                          **kwargs)
