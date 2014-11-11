from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_user
from django.contrib.auth import logout
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import redirect
from django.views.generic import FormView, View

from ftp_deploy.server.forms import LoginForm


class loginView(FormView):

    """View for login"""

    form_class = LoginForm
    template_name = 'ftp_deploy/login/login.html'
    success_url = reverse_lazy('ftpdeploy_dashboard')

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return HttpResponseRedirect(reverse('ftpdeploy_dashboard'))
        return super(loginView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login_user(self.request, user)
        else:
            messages.error(self.request, 'Username or Password incorrect.')
            return HttpResponseRedirect(reverse('ftpdeploy_login'))
        return super(loginView, self).form_valid(form)


class logoutView(View):

    """View for logout"""

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse('ftpdeploy_login'))
