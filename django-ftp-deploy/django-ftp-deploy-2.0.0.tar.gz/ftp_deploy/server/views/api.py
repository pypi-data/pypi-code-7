
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin

from braces.views import JSONResponseMixin, LoginRequiredMixin

from ftp_deploy.conf import *
from ftp_deploy.models import Service
from ftp_deploy.utils.repo import repository_api


class RepoAPIView(LoginRequiredMixin, JSONResponseMixin, SingleObjectMixin,
                  View):

    """View for managing BitBucket API"""

    model = Service

    def dispatch(self, request, repo, *args, **kwargs):
        self.repo_api = repository_api(repo)
        return super(RepoAPIView, self).dispatch(request, repo, * args,
                                                 **kwargs)

    def post(self, request, repo, *args, **kwargs):
        if self.request.POST['data'] == 'respositories':
            context = self.repo_api.repositories()
        elif self.request.POST['data'] == 'addhook':
            context = self.repo_api.add_hook(self.get_object(), request)

        return self.render_json_response(context)
