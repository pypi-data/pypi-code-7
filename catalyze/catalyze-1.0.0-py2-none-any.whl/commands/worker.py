from __future__ import absolute_import

import click
from catalyze import cli, client, project

@cli.command(short_help = "Start a background worker.")
@click.argument("target", default = "worker")
def worker(target):
    settings = project.read_settings()
    session = client.acquire_session(settings)
    target = args[0] if len(args) > 0 else "worker"
    print("Initiating a background worker for Service: %s (procfile target = \"%s\")" % (session['serviceId'], target))
    services.initiate_worker(session, settings["environmentId"], settings["serviceId"], target)
