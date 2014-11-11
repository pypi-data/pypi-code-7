from __future__ import absolute_import

from .celery import app
from .utils.deploy import Deploy


@app.task
def deploy_task(host, payload, service):
    deploy = Deploy(host, payload, service, deploy_task.request.id)
    deploy.perform()
