from copy import deepcopy
import collections
import addressable
import inspector
import utils
import account
import columns


class Report(object):
    def __init__(self, raw, query):
        self.raw = []
        self.queries = []

        registry = query.profile.webproperty.account.columns
        headers = [registry[header['name']] for header in raw['columnHeaders']]
        slugs = [header.pyslug for header in headers]
        self.row_cls = collections.namedtuple('Row', slugs)
        self.headers = addressable.List(headers, 
            indices=registry.indexed_on, insensitive=True)
        self.rows = []
        self.append(raw, query)

    def append(self, raw, query):
        self.raw.append(raw)
        self.queries.append(query)
        self.is_complete = not 'nextLink' in raw

        casters = [column.cast for column in self.headers]

        # if no rows were returned, the GA API doesn't 
        # include the `rows` key at all
        for row in self.raw[-1].get('rows', []):
            typed_row = [casters[i](row[i]) for i in range(len(self.headers))]
            typed_tuple = self.row_cls(*typed_row)
            self.rows.append(typed_tuple)

        # TODO: figure out how this works with paginated queries
        self.totals = raw['totalsForAllResults']
        # more intuitive when querying for just a single metric
        self.total = raw['totalsForAllResults'].values()[0]
        # print self.totals

    def serialize(self):
        serialized = []
        for row in self.rows:
            row = row._asdict()
            for key, value in row.items():
                row[key] = utils.simplify(value)
            serialized.append(row)
        return serialized

    def __getitem__(self, key):
        try:
            i = self.headers.index(key)
            return [row[i] for row in self.rows]
        except ValueError:
            raise ValueError(key + " not in column headers")

    def __iter__(self):
        raise NotImplementedError()

    def __len__(self):
        return len(self.rows)


def condition(value):
    return "condition::" + value

def sequence(value):
    return "sequence::" + value

def all(*values):
    return condition(";".join(values))

def any(*values):
    return condition(",".join(values))

def followed_by(*values):
    return sequence(";->>".join(values))

def immediately_followed_by(*values):
    return sequence(";->".join(values))


class Query(object):
    def __init__(self, profile, metrics=[], dimensions=[], meta={}, title=None):
        self._title = title
        self.raw = {'ids': 'ga:' + profile.id}
        self.meta = {}
        self.meta.update(meta)
        self.profile = profile
        self.webproperty = profile.webproperty
        self.account = profile.webproperty.account
        self._specify(metrics=metrics, dimensions=dimensions)

    def _serialize_criterion(criterion):
        pattern = r'(?P<identifier>[\w:]+)((?P<operator>[\!\=\>\<\@\~]+)(?P<value>[\w:]+))?'
        match = re.match(pattern, criterion)
        identifier = match.group('identifier')
        operator = match.group('operator') or ''
        value = match.group('value') or ''
        column = self._serialize_column(identifier)
        return column + operator + value

    def _normalize_column(self, value):
        if isinstance(value, account.Column):
            return value
        else:
            return self.account.columns[value]

    def _serialize_column(self, value):
        return self._normalize_column(value).id

    def _serialize_columns(self, values):
        if not isinstance(values, (list, tuple)):
            values = [values]

        return [self._serialize_column(value) for value in values]

    def _normalize_segment(self, value):
        if isinstance(value, account.Segment):
            return value
        else:
            return self.account.segments[value]
    
    def _serialize_segment(self, value):
        return self._normalize_segment(value).id

    def _serialize(self, obj):
        if isinstance(obj, list):
            return [self._serialize(el) for el in obj]
        elif isinstance(obj, account.Column):
            return obj.id
        else:
            return obj

    def clone(self):
        query = self.__class__(profile=self.profile, meta=self.meta)
        query.raw = deepcopy(self.raw)
        return query

    @utils.immutable
    def set(self, key=None, value=None, **kwargs):
        """
        `set` is a way to add raw properties to the request, 
        for features that python-google-analytics does not 
        support or supports incompletely. For convenience's 
        sake, it will serialize Column objects but will 
        leave any other kind of value alone.
        """

        if key and value:
            self.raw[key] = self._serialize(value)
        elif key or kwargs:
            properties = key or kwargs
            for key, value in properties.items():
                self.raw[key] = self._serialize(value)
        else:
            raise ValueError(
                "Query#set requires a key and value, a properties dictionary or keyword arguments.")

        return self

    def _specify(self, metrics=[], dimensions=[]):
        metrics = self._serialize_columns(metrics)
        dimensions = self._serialize_columns(dimensions)
        self.raw.setdefault('metrics', []).extend(metrics)
        self.raw.setdefault('dimensions', []).extend(dimensions)

        return self

    @property
    def description(self):
        """
        A list of the metrics this query will ask for.
        """

        if len(self.raw['metrics']):
            metrics = self.raw['metrics']
            head = metrics[0:-1] or metrics[0:1]
            text = ", ".join(head)
            if len(metrics) > 1:
                tail = metrics[-1]
                text = text + " and " + tail
        else:
            text = 'n/a'

        return text

    @property
    def title(self):
        return self._title or self.description

    @title.setter
    def title(self, value):
        self._title = value

    @inspector.implements(_specify)
    @utils.immutable
    def query(self, *vargs, **kwargs):
        """
        Return a new query with additional metrics and dimensions.
        If specifying only a single metric or dimension, you can 
        but are not required to wrap it in a list.

        This interface is identical to the one you use to construct
        new queries, `Profile#query`. Look there for more details.
        """
        return self._specify(*vargs, **kwargs)

    @utils.immutable
    def metrics(self, *metrics):
        """
        Return a new query with additional metrics.

        ```python
        query.metrics('pageviews', 'page load time')
        ```
        """
        return self._specify(metrics=metrics)

    @utils.immutable
    def dimensions(self, *dimensions):
        """
        Return a new query with additional dimensions.

        ```python
        query.dimensions('search term', 'search depth')
        ```
        """
        return self._specify(dimensions=dimensions)

    @utils.immutable
    def sort(self, *columns):
        """
        Return a new query which will produce results sorted by 
        one or more metrics or dimensions. You may use plain 
        strings for the columns, or actual `Column`, `Metric` 
        and `Dimension` objects.

        Add a minus in front of the metric (either the string or 
        the object) to sort in descending order.

        ```python
        # sort using strings
        query.sort('pageviews', '-device type')

        # sort using metric, dimension or column objects
        pageviews = account.metrics['pageviews']
        query.sort(-pageviews)
        ```
        """

        sorts = []

        for column in columns:          
            if isinstance(column, account.Column):
                ascending = False
                identifier = column.id
            elif isinstance(column, basestring):
                ascending = column.startswith('-')
                identifier = self.account.columns[column.lstrip('-')].id
            else:
                raise ValueError()

            if ascending:
                sign = '-'
            else:
                sign = ''

            sorts.append(sign + identifier) 

        self.raw['sort'] = ",".join(sorts)
        return self

    @utils.immutable
    def filter(self, value):
        """ Most of the actual functionality lives on the Column 
        object and the `all` and `any` functions. """
        self.raw['filters'] = value


class CoreQuery(Query):
    """
    CoreQuery is the main way through which to produce reports
    from data in Google Analytics.

    The most important methods are:

    * `metrics` and `dimensions` (both of which you can also pass as 
      lists when creating the query)
    * `range` and its shortcuts that have the granularity already set: 
      `hourly`, `daily`, `weekly`, `monthly`, `yearly`
    * `filter` to filter which rows are analyzed before running the query
    * `segment` to filter down to a certain kind of session or user (as 
      opposed to `filter` which works on individual rows of data)
    * `limit` to ask for a subset of results
    * `sort` to sort the query


    CoreQuery is mostly immutable: wherever possible, methods 
    return a new query rather than modifying the existing one,
    so for example this works as you'd expect it to:

    ```python
    base = profile.query('pageviews')
    january = base.daily('2014-01-01', months=1).execute()
    february = base.daily('2014-02-01', months=1).execute()
    ```
    """

    # TODO (?)
    # fields
    # userIp / quotaUser
    # https://developers.google.com/analytics/devguides/reporting/core/v3/reference#q_summary

    PRECISION_LEVELS = ('FASTER', 'DEFAULT', 'HIGH_PRECISION', )
    GRANULARITY_LEVELS = ('year', 'month', 'week', 'day', 'hour', )
    GRANULARITY_DIMENSIONS = (
        'ga:year', 'ga:yearMonth', 'ga:yearWeek', 
        'ga:date', 'ga:dateHour',
    )

    @utils.immutable
    def range(self, start, stop=None, months=0, days=0, precision=1, granularity=None):
        """
        Return a new query that fetches metrics within a certain date range.

        ```python
        query.range('2014-01-01', '2014-06-30')
        ```

        If you don't specify a `stop` argument, the date range will end today. If instead 
        you meant to fetch just a single day's results, try: 

        ```python
        query.range('2014-01-01', days=1)
        ```

        More generally, you can specify that you'd like a certain number of days, 
        starting from a certain date:

        ```python
        query.range('2014-01-01', months=3)
        query.range('2014-01-01', days=28)
        ```

        Note that if you don't specify a granularity (either through the `granularity`
        argument or through the `hourly`, `daily`, `weekly`, `monthly` or `yearly`
        shortcut methods) you will get only a single result, encompassing the 
        entire date range, per metric.

        For queries that should run faster, you may specify a lower precision, 
        and for those that need to be more precise, a higher precision:

        ```
        # faster queries
        query.range('2014-01-01', '2014-01-31', precision=0)
        query.range('2014-01-01', '2014-01-31', precision='FASTER')
        # queries with the default level of precision (usually what you want)
        query.range('2014-01-01', '2014-01-31')
        query.range('2014-01-01', '2014-01-31', precision=1)
        query.range('2014-01-01', '2014-01-31', precision='DEFAULT')
        # queries that are more precise
        query.range('2014-01-01', '2014-01-31', precision=2)
        query.range('2014-01-01', '2014-01-31', precision='HIGH_PRECISION')        
        ```

        **Note:** it is currently not possible to easily specify that you'd like 
        to query the last last full week or weeks. This will be added sometime
        in the future.

        As a stopgap measure, it is possible to use the [`nDaysAgo` format][query]
        format for your start date.

        [query]: https://developers.google.com/analytics/devguides/reporting/core/v3/reference#q_summary
        """
        start, stop = utils.daterange(start, stop, months, days)

        self.raw.update({
            'start_date': start, 
            'end_date': stop, 
        })

        if isinstance(precision, int):
            precision = self.PRECISION_LEVELS[precision]

        if precision not in self.PRECISION_LEVELS:
            levels = ", ".join(self.PRECISION_LEVELS)
            raise ValueError("Granularity should be one of: " + levels)

        if precision != 'DEFAULT':
            self.raw.update({'samplingLevel': precision})

        if granularity:
            if not isinstance(granularity, int):
                if granularity in self.GRANULARITY_LEVELS:
                    granularity = self.GRANULARITY_LEVELS.index(granularity)
                else:
                    levels = ", ".join(options.keys())
                    raise ValueError("Granularity should be one of: " + levels)

            dimension = self.GRANULARITY_DIMENSIONS[granularity]
            self.raw['dimensions'].insert(0, dimension)

        return self

    @inspector.implements(range)
    def hourly(self, *vargs, **kwargs):
        kwargs['granularity'] = 'hour'
        return self.range(*vargs, **kwargs)

    @inspector.implements(range)
    def daily(self, *vargs, **kwargs):
        """
        Return a new query that fetches metrics within a certain date 
        range, summarized by day. This method is identical to 
        `CoreQuery#range` but it sets the default granularity to 
        `granularity='day'`.
        """

        kwargs['granularity'] = 'day'
        return self.range(*vargs, **kwargs)

    @inspector.implements(range)
    def weekly(self, *vargs, **kwargs):
        """
        Return a new query that fetches metrics within a certain date 
        range, summarized by week. This method is identical to 
        `CoreQuery#range` but it sets the default granularity to 
        `granularity='week'`.
        """

        kwargs['granularity'] = 'week'
        return self.range(*vargs, **kwargs)

    @inspector.implements(range)
    def monthly(self, *vargs, **kwargs):
        """
        Return a new query that fetches metrics within a certain date 
        range, summarized by month. This method is identical to 
        `CoreQuery#range` but it sets the default granularity to 
        `granularity='month'`.
        """

        kwargs['granularity'] = 'month'
        return self.range(*vargs, **kwargs)

    @inspector.implements(range)
    def yearly(self, *vargs, **kwargs):
        """
        Return a new query that fetches metrics within a certain date 
        range, summarized by year. This method is identical to 
        `CoreQuery#range` but it sets the default granularity to 
        `granularity='year'`.
        """

        kwargs['granularity'] = 'year'
        return self.range(*vargs, **kwargs)

    @utils.immutable
    def step(self, maximum):
        """
        Return a new query with a maximum amount of results to be returned 
        in any one request, without implying that we should stop 
        fetching beyond that limit (unlike `CoreQuery#limit`.)

        Useful in debugging pagination functionality.

        Perhaps also useful when you  want to be able to decide whether to
        continue fetching data, based  on the data you've already received.
        """

        self.raw['max_results'] = maximum
        return self

    @utils.immutable
    def limit(self, *_range):
        """
        Return a new query, limited to a certain number of results.

        ```python
        # first 100
        query.limit(100)
        # 50 to 60
        query.limit(50, 10)
        ```

        Please note carefully that Google Analytics uses 
        1-indexing on its rows.
        """

        # uses the same argument order as 
        # LIMIT in a SQL database
        if len(_range) == 2:
            start, maximum = _range
        else:
            start = 1
            maximum = _range[0]

        self.meta['limit'] = maximum

        self.raw.update({
            'start_index': start, 
            'max_results': maximum, 
        })
        return self

    @utils.immutable
    def segment(self, value, type=None):
        """
        Return a new query, limited to a segment of all users or sessions.

        Accepts segment objects, filtered segment objects and segment names:

        ```python
        query.segment(account.segments['browser'])
        query.segment('browser')
        query.segment(account.segments['browser'].any('Chrome', 'Firefox'))
        ```

        Segment can also accept a segment expression when you pass 
        in a `type` argument. The type argument can be either `users`
        or `sessions`. This is pretty close to the metal.

        ```python
        # will be translated into `users::condition::perUser::ga:sessions>10`
        query.segment('condition::perUser::ga:sessions>10', type='users')
        ```

        See the [Google Analytics dynamic segments documentation][segments]

        You can also use the `any`, `all`, `followed_by` and 
        `immediately_followed_by` functions in this module to 
        chain together segments.

        Everything about how segments get handled is still in flux.
        Feel free to propose ideas for a nicer interface on 
        the [GitHub issues page][issues]

        [segments]: https://developers.google.com/analytics/devguides/reporting/core/v3/segments#reference
        [issues]: https://github.com/debrouwere/google-analytics/issues
        """

        # TODO / NOTE: support for dynamic segments using 
        # conditions and sequences is barebones at the moment
        if type:
            value = "{type}::{value}".format(type=type, value=value)
        else:
            value = self._serialize_segment(value)

        self.raw['segment'] = value
        return self

    def live(self):
        """
        Turn a regular query into one for the live API.

        **Note:** a placeholder, not implemented yet.
        """
        # add in metrics, dimensions, sort, filters
        raise NotImplementedError()
        return RealTimeQuery(metrics=self.metrics, dimensions=self.dimensions)

    @utils.immutable
    def next(self):
        """
        Return a new query with a modified `start_index`.
        Mainly used internally to paginate through results.
        """
        step = self.raw.get('max_results', 1000)
        start = self.raw.get('start_index', 1) + step
        self.raw['start_index'] = start
        return self

    def _execute(self):
        raw = deepcopy(self.raw)
        raw['metrics'] = ','.join(self.raw['metrics'])
        raw['dimensions'] = ','.join(self.raw['dimensions'])

        service = self.account.service
        response = service.data().ga().get(**raw).execute()
        
        return Report(response, self)        

    def execute(self):
        """
        Run the query and return a `Report`.

        Execute transparently handles paginated results, so even for results that 
        are larger than the maximum amount of rows the Google Analytics API will 
        return in a single request, or larger than the amount of rows as specified 
        through `CoreQuery#step`,  execute will leaf through all pages,  
        concatenate the results and produce a single Report instance.
        """

        cursor = self
        report = None
        is_complete = False
        is_enough = False

        while not (is_enough or is_complete):
            chunk = cursor._execute()

            if report:
                report.append(chunk.raw[0], cursor)
            else:
                report = chunk

            is_enough = len(report.rows) >= self.meta.get('limit', float('inf'))
            is_complete = chunk.is_complete
            cursor = cursor.next()

        return report

    def __repr__(self):
        return "<Query: {} ({})>".format(self.title, self.profile.name)


class RealTimeQuery(Query):
    """
    A query against the [Google Analytics Live API][live].

    **Note:** a placeholder, not implemented yet.

    [live]: https://developers.google.com/analytics/devguides/reporting/realtime/v3/reference/data/realtime#resource
    """


def describe(profile, description):
    """
    Generate a query by describing it as a series of actions 
    and parameters to those actions. These map directly 
    to Query methods and arguments to those methods.

    This is an alternative to the chaining interface.
    Mostly useful if you'd like to put your queries
    in a file, rather than in Python code.
    """
    return refine(profile.query(), description)

def refine(query, description):
    """
    Refine a query from a dictionary of parameters that describes it.
    See `describe` for more information.
    """

    for attribute, arguments in description.items():
        if hasattr(query, attribute):
            attribute = getattr(query, attribute)
        else:
            raise ValueError("Unknown query method: " + attribute)

        if callable(attribute):
            method = attribute
            if isinstance(arguments, dict):
                query = method(**arguments)
            elif isinstance(arguments, list):
                query = method(*arguments)
            else:
                query = method(arguments)
        else:
            setattr(attribute, arguments)
            
    return query
