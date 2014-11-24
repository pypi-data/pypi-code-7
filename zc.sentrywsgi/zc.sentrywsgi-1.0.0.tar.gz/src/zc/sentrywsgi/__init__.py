import corbeau
import logging
import raven
import raven.conf
import raven.handlers.logging
import raven.middleware
import requests.adapters

# work around stale connection issue in urllib3
# https://github.com/shazow/urllib3/issues/245
adapter = requests.adapters.HTTPAdapter(max_retries=1)
corbeau.session.mount("http://", adapter)
corbeau.session.mount("https://", adapter)


Client = lambda dsn, **options: corbeau.Client(dsn, **options)


def configure_logging(client):
    handler = raven.handlers.logging.SentryHandler(client, level=logging.ERROR)
    raven.conf.setup_logging(handler)


def filter_factory(app, global_conf, **kwargs):
    client = Client(**kwargs)
    configure_logging(client)
    return raven.middleware.Sentry(app, client)
