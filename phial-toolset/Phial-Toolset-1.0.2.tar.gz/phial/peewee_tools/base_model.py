# -*- coding: utf-8 -*-
try:
    from peewee import logger
    from playhouse.proxy import Proxy
    try:
        from playhouse.gfk import Model
    except ImportError:
        print('[Phial][WARN] playhouse.gfk not found. Generic ForeignKey not supported!')
        from peewee import Model
except ImportError:
    BaseModel = None
    gl_database_type = -1
    gl_database = None
else:
    import logging

    # Inhib peewee log
    logger.addHandler(logging.NullHandler())

    # Database type
    gl_database      = Proxy()
    gl_database_type = -1

    class   BaseModel(Model):
        class       Meta:
            database = gl_database
