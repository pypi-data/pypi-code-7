from __future__ import absolute_import
from celery import shared_task
from .models import BitBucketRepo
from .utils import process_commits


@shared_task
def celery_process_commits(repo_pk, json_data):
    ''' Celery wrapper for utils.process_commits
    '''
    try:
        repo = BitBucketRepo.objects.get(pk=repo_pk)
    except BitBucketRepo.DoesNotExist:
        return
    process_commits(repo, json_data)
