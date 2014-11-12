
import ast
import json
import arrow
import logging
import elasticsearch

from bson import ObjectId
from eve.utils import config
from eve.io.base import DataLayer

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


logger = logging.getLogger(__name__)


def parse_date(date_str):
    """Parse elastic datetime string."""
    try:
        date = arrow.get(date_str)
    except TypeError:
        date = arrow.get(date_str[0])
    return date.datetime


def get_dates(schema):
    """Return list of datetime fields for given schema."""
    dates = [config.LAST_UPDATED, config.DATE_CREATED]
    for field, field_schema in schema.items():
        if field_schema['type'] == 'datetime':
            dates.append(field)
    return dates


def format_doc(hit, schema, dates):
    """Format given doc to match given schema."""
    doc = hit.get('_source', {})
    doc.setdefault(config.ID_FIELD, hit.get('_id'))
    doc.setdefault('_type', hit.get('_type'))

    for key in dates:
        if key in doc:
            doc[key] = parse_date(doc[key])

    return doc


def is_elastic(datasource):
    """Detect if given resource uses elastic."""
    return datasource.get('backend') == 'elastic' or datasource.get('search_backend') == 'elastic'


class ElasticJSONSerializer(elasticsearch.JSONSerializer):
    """Customize the JSON serializer used in Elastic"""
    def default(self, value):
        """Convert mongo.ObjectId."""
        if isinstance(value, ObjectId):
            return str(value)
        return super().default(value)


class ElasticCursor(object):
    """Search results cursor."""

    no_hits = {'hits': {'total': 0, 'hits': []}}

    def __init__(self, hits=None, docs=None):
        """Parse hits into docs."""
        self.hits = hits if hits else self.no_hits
        self.docs = docs if docs else []

    def __getitem__(self, key):
        return self.docs[key]

    def first(self):
        """Get first doc."""
        return self.docs[0] if self.docs else None

    def count(self, **kwargs):
        """Get hits count."""
        return int(self.hits['hits']['total'])

    def extra(self, response):
        """Add extra info to response."""
        if 'facets' in self.hits:
            response['_facets'] = self.hits['facets']


def set_filters(query, *args):
        """Combine given filters."""
        filters = [x for x in args if x is not None]
        if filters:
            query['filter'] = {'and': filters}


def set_sort(query, sort):
    query['sort'] = []
    for (key, sortdir) in sort:
        sort_dict = dict([(key, 'asc' if sortdir > 0 else 'desc')])
        query['sort'].append(sort_dict)


class Elastic(DataLayer):
    """ElasticSearch data layer."""

    serializers = {
        'integer': int,
        'datetime': parse_date,
        'objectid': ObjectId,
    }

    def init_app(self, app):
        app.config.setdefault('ELASTICSEARCH_URL', 'http://localhost:9200/')
        app.config.setdefault('ELASTICSEARCH_INDEX', 'eve')

        self.index = app.config['ELASTICSEARCH_INDEX']
        url = urlparse(app.config['ELASTICSEARCH_URL'])
        self.es = elasticsearch.Elasticsearch(hosts=[{'host': url.hostname, 'port': url.port}])
        self.es.transport.serializer = ElasticJSONSerializer()
        self.es_indices = elasticsearch.client.IndicesClient(self.es)

        try:
            self.es_indices.create(self.index)
        except elasticsearch.TransportError:
            pass

        self.put_mapping(app)

    def _get_field_mapping(self, schema):
        """Get mapping for given field schema."""
        if schema['type'] == 'datetime':
            return {'type': 'date'}
        elif schema['type'] == 'string' and schema.get('unique'):
            return {'type': 'string', 'index': 'not_analyzed'}

    def put_mapping(self, app):
        """Put mapping for elasticsearch for current schema.

        It's not called automatically now, but rather left for user to call it whenever it makes sense.
        """
        for resource, resource_config in app.config['DOMAIN'].items():
            datasource = resource_config.get('datasource', {})

            if not is_elastic(datasource):
                continue

            if datasource.get('source', resource) != resource:  # only put mapping for core types
                continue

            properties = {}
            properties[config.DATE_CREATED] = self._get_field_mapping({'type': 'datetime'})
            properties[config.LAST_UPDATED] = self._get_field_mapping({'type': 'datetime'})

            for field, schema in resource_config['schema'].items():
                field_mapping = self._get_field_mapping(schema)
                if field_mapping:
                    properties[field] = field_mapping

            mapping = {'properties': properties}
            self.es_indices.put_mapping(index=self.index, doc_type=resource, body=mapping, ignore_conflicts=True)

    def find(self, resource, req, sub_resource_lookup):
        args = getattr(req, 'args', {})

        if args.get('source'):
            query = json.loads(args.get('source'))
            if 'filtered' not in query.get('query', {}):
                _query = query.get('query')
                query['query'] = {'filtered': {}}
                if _query:
                    query['query']['filtered']['query'] = _query
        else:
            query = {'query': {'filtered': {}}}

        if args.get('q', None):
            query['query']['filtered']['query'] = {
                'query_string': {
                    'query': args.get('q'),
                    'default_field': args.get('df', '_all'),
                    'default_operator': 'AND',
                    }
                }

        # use default sort when there is no sort set
        if not req.sort and self._default_sort(resource):
            set_sort(query, self._default_sort(resource))

        # skip sorting when there is a query to use score
        if req.sort and 'q' not in args:
            sort = ast.literal_eval(req.sort)
            set_sort(query, sort)

        if req.max_results:
            query['size'] = req.max_results

        if req.page > 1:
            query['from'] = (req.page - 1) * req.max_results

        source_config = config.SOURCES[resource]

        # filter
        query_filter = query.get('filter')
        resource_filter = source_config.get('elastic_filter')
        sub_resource_filter = {'term': sub_resource_lookup} if sub_resource_lookup else None
        set_filters(query, resource_filter, query_filter, sub_resource_filter)

        if 'facets' in source_config:
            query['facets'] = source_config['facets']

        args = self._es_args(resource)
        hits = self.es.search(body=query, **args)
        return self._parse_hits(hits, resource)

    def find_one(self, resource, req, **lookup):

        def is_found(hit):
            if 'exists' in hit:
                hit['found'] = hit['exists']
            return hit.get('found', False)

        args = self._es_args(resource)

        if config.ID_FIELD in lookup:
            try:
                hit = self.es.get(id=lookup[config.ID_FIELD], **args)
            except elasticsearch.NotFoundError:
                return

            if not is_found(hit):
                return

            docs = self._parse_hits({'hits': {'hits': [hit]}}, resource)
            return docs.first()
        else:
            query = {
                'query': {
                    'term': lookup
                }
            }

            try:
                args['size'] = 1
                hits = self.es.search(body=query, **args)
                docs = self._parse_hits(hits, resource)
                return docs.first()
            except elasticsearch.NotFoundError:
                return

    def find_one_raw(self, resource, _id):
        args = self._es_args(resource)
        hit = self.es.get(id=_id, **args)
        return self._parse_hits({'hits': {'hits': [hit]}}, resource).first()

    def find_list_of_ids(self, resource, ids, client_projection=None):
        args = self._es_args(resource)
        return self._parse_hits(self.es.multi_get(ids, **args), resource)

    def insert(self, resource, doc_or_docs, **kwargs):
        ids = []
        kwargs.update(self._es_args(resource, refresh=True))
        for doc in doc_or_docs:
            doc.update(self.es.index(body=doc, id=doc.get('_id'), **kwargs))
            ids.append(doc['_id'])
        return ids

    def update(self, resource, id_, updates):
        args = self._es_args(resource, refresh=True)
        return self.es.update(id=id_, body={'doc': updates}, **args)

    def replace(self, resource, id_, document):
        args = self._es_args(resource, refresh=True)
        return self.es.index(body=document, id=id_, **args)

    def remove(self, resource, lookup=None):
        args = self._es_args(resource)
        if lookup:
            try:
                return self.es.delete(id=lookup.get('_id'), refresh=True, **args)
            except elasticsearch.NotFoundError:
                return
        else:
            query = {'query': {'match_all': {}}}
            return self.es.delete_by_query(body=query, **args)

    def is_empty(self, resource):
        args = self._es_args(resource)
        res = self.es.count(body={'query': {'match_all': {}}}, **args)
        return res.get('count', 0) == 0

    def get_mapping(self, index, doc_type=None):
        return self.es_indices.get_mapping(index=index, doc_type=doc_type)

    def _parse_hits(self, hits, resource):
        """Parse hits response into documents."""
        datasource = self._datasource(resource)
        schema = config.DOMAIN[datasource[0]]['schema']
        dates = get_dates(schema)
        docs = []
        for hit in hits.get('hits', {}).get('hits', []):
            docs.append(format_doc(hit, schema, dates))
        return ElasticCursor(hits, docs)

    def _es_args(self, resource, refresh=None):
        """Get index and doctype args."""
        datasource = self._datasource(resource)
        args = {
            'index': self.index,
            'doc_type': datasource[0],
            }
        if refresh:
            args['refresh'] = refresh
        return args

    def _fields(self, resource):
        """Get projection fields for given resource."""
        datasource = self._datasource(resource)
        keys = datasource[2].keys()
        return ','.join(keys) + ','.join([config.LAST_UPDATED, config.DATE_CREATED])

    def _default_sort(self, resource):
        datasource = self._datasource(resource)
        return datasource[3]
