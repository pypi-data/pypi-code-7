import os
import hashlib
import json

from flask import Blueprint, current_app

import json_resource

from . import resources
from . import views


class FlaskResourceMixin(object):
    """ Mixin for resources that are exposed through flask-json-resource."""
    @property
    def etag(self):
        """ Add etag to the resource."""
        return hashlib.md5(json.dumps(self)).hexdigest()

    @classmethod
    def collection(cls):
        """ Mongo Collection to use for storing / querying users.

        Use the pymongo connection for this.
        """
        db = current_app.extensions['json_resource'].db

        return db[cls.schema['id']]


class API(object):
    """ Flask extension for exposing `json-resource` resources as a RESTful
    api.

    To set up your api, simply create a `Flask` app, and a `flask-pymongo`
    database:

    >>> app = Flask('test')
    >>> app.debug = True

    >>> db = PyMongo(app)
    >>> api = API(app, db)

    After initialization, you can register resources to this API:

    >>> @api.register()
        class TestResource(api.Resource):
            schema = Schema({'id': 'test-resource'})

    The schema of the resource will automatically be loaded from the `schems`
    directory in your package.
    """
    def __init__(self, import_name, app=None, db=None, *args, **kwargs):
        """ Create an new flask-json-resource API.
        """
        self.resources = []
        self.blueprint = Blueprint('json_resource', import_name)

        resources.Schema.register_schema_dir(
            os.path.join(self.blueprint.root_path, 'schemas')
        )

        self.register()(resources.Schema)

        class Resource(FlaskResourceMixin, json_resource.Resource):
            default_views = (
                views.ResourceView, views.ResourceCreateView
            )

        class Collection(FlaskResourceMixin, json_resource.Collection):
            default_views = (views.CollectionView, )

        self.Resource = Resource
        self.Collection = Collection

        if app:
            self.init_app(app, db)

    def init_app(self, app, mongo):
        """Initialize the extension with a flask app and a pymongo db.

        This allows for the deferred extension loading pattern in flask.
        """
        if not hasattr(app, 'extensions'):
            app.extensions = {}

        app.extensions['json_resource'] = self

        app.register_blueprint(self.blueprint)

        with app.app_context():
            background = not app.debug

            for resource in self.resources:
                if not hasattr(resource, 'indexes'):
                    continue

                for index in resource.indexes:
                    resource.collection().ensure_index(
                        index['key'],
                        unique=index.get('unique'),
                        background=background
                    )

        self.mongo = mongo

    @property
    def db(self):
        """ The mongo database that is used to store the resource."""
        return self.mongo.db

    def register(self, views=None, authorization=None):
        """ Register a resource with the api.

        This can be used as a decorator:

        >>> @api.register()
        class TestResource(api.Resource):
            schema = Schema({'id': 'test-resource'})

        By default, a ResourceView is registered for the resource. If the resources
        schema has a `create` link, a ResourceCreation view is also registered

        It is possible to override the views that are registered for this
        resource:

        >>> @api.register(views=views.TestResourceView)
        class TestResource(api.Resource):
            schema = Schema({'id': 'test-resource'})
        """
        def _register(resource_cls):
            self.resources.append(resource_cls)

            _views = views or resource_cls.default_views

            for view in _views:
                if authorization:
                    view = view(resource_cls, authorization())
                else:
                    view = view(resource_cls)

                if view.route:
                    self.blueprint.route(view.route, **view.options)(view)

            return resource_cls

        return _register
