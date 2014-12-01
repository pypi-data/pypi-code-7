import json
from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from .models import Q, BitBucketRepo
from .utils import process_commits
from . import settings

if settings.USE_CELERY:
    from .tasks import celery_process_commits
else:
    celery_process_commits = None


def trello_distribute(repo, json_data):
    ''' Helper function that decides how to process
        Trello interaction (celery or not)
    '''
    if celery_process_commits is not None:
        celery_process_commits.delay(repo.pk, json_data)
    else:
        process_commits(repo, json_data)


class BitBucketPostView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponseBadRequest()

    def post(self, request, *args, **kwargs):
        if settings.RESTRICT_IPS:
            if request.META['REMOTE_ADDR'] not in settings.BITBUCKET_IPS:
                return HttpResponseBadRequest()

        try:
            json_data = json.loads(request.POST['payload'])
            repo_slug = json_data['repository']['slug']
        except (ValueError, KeyError) as e:
            return HttpResponseBadRequest()

        query = Q(slug=repo_slug) & \
                Q(access_key=request.REQUEST.get('access_key', ''))
        repo = get_object_or_404(BitBucketRepo, query)
        trello_distribute(repo, json_data)
        return HttpResponse('OK')

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(BitBucketPostView, self).dispatch(*args, **kwargs)
