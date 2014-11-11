from __future__ import absolute_import
import json
from celery.result import AsyncResult

from django.views.generic.base import View
from django.http import HttpResponse, JsonResponse, Http404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import Service, Task
from .tasks import deploy_task
from .utils.core import absolute_url
from .utils.repo import repository_parser


class DeployView(View):

    """Main view receive POST Hook from repository"""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        try:
            self.service = Service.objects.get(secret_key=kwargs['secret_key'])
        except Exception:
            raise Http404

        self.service_pk = str(self.service.pk)
        return super(DeployView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        json_string = request.POST['payload'].replace('\n', '')
        data = json.loads(json_string)

        if(repository_parser(data, self.service).check_branch()):
            host = absolute_url(request).build()
            job = deploy_task.apply_async((host, json_string, self.service),
                                          countdown=1)
            Task.objects.create(name=job.id, service=self.service)

        return HttpResponse(status=200)


class DeployStatusView(DeployView):

    def post(self, request, *args, **kwargs):
        data = dict()
        if self.service.has_queue():
            task_id = self.service.task_set.all()[0]
            task = AsyncResult(task_id.name)
            data = task.result or dict(status=task.state)

        data['queue'] = self.service.task_set.all().count()
        return JsonResponse(data)
