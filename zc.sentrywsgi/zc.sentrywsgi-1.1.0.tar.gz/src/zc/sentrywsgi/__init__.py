import logging
import raven
import raven.conf
import raven.handlers.logging
import raven.middleware


def configure_logging(client):
    handler = raven.handlers.logging.SentryHandler(client, level=logging.ERROR)
    raven.conf.setup_logging(handler)


def filter_factory(app, global_conf, **kwargs):
    client = raven.Client(**kwargs)
    configure_logging(client)
    return raven.middleware.Sentry(app, client)
