import requests
import json

from django.conf import settings
from django.db import transaction
from django.core.management.base import BaseCommand
from flis_metadata.common.models import get_replicated_models

from requests.exceptions import ConnectionError


class RemoteException(Exception):
    pass


class MaxRequestsReached(Exception):
    pass


MAX_REQUESTS = 100


def get_model_endpoint(name):
    host, path = settings.METADATA_REMOTE_HOST, settings.METADATA_REMOTE_PATH
    return '{0}{1}/api/v1/{2}/?format=json'.format(host, path, name.lower())


def get_model_instances(name, model):
    """For a given model get all instances using the remote API."""
    endpoint = get_model_endpoint(name)

    objects = []
    for _ in xrange(MAX_REQUESTS):
        try:
            response = requests.get(endpoint)
        except ConnectionError:
            raise RemoteException(
                'Error reaching remote endpoint: {0}'.format(endpoint))

        if response.status_code != 200:
            raise RemoteException(
                'Bad response for endpoint: {0}'.format(endpoint))

        response_obj = json.loads(response.text)

        objects += response_obj['objects']
        if not response_obj['meta']['next']:
            break

        endpoint = settings.METADATA_REMOTE_HOST + response_obj['meta']['next']
    else:
        raise MaxRequestsReached()

    # Remove default resource_uri field
    for o in objects:
        o.pop('resource_uri')

    return objects


@transaction.atomic
def update_model_instances(name, model):
    """Update local model for model data from remote instances."""
    instances = get_model_instances(name, model)

    for instance in instances:
        obj = model(**instance)
        obj.save()


class Command(BaseCommand):
    help = 'Sync remote models on local database'

    def handle(self, *args, **options):
        for name, model in get_replicated_models():
            print 'Syncing {0}: ...'.format(name),
            update_model_instances(name, model)
            print 'done!'
