from django import template

def _order_by(queryset, value):
    args = value.split(',')
    return queryset.order_by(*args)

def _offset(queryset, value):
    value = int(value)
    return queryset[value:]

def _limit(queryset, value):
    value = int(value)
    return queryset[:value]

QUERYSET_OPTIONS_CALLBACK = {
    'order_by': _order_by,
    'offset': _offset,
    'limit': _limit,
}


class ValidationError(Exception):
    pass


def parse_queryset_option_value(value):
    '''
    Options that get parsed:

    datetime(now)
    datetime(2009-02-23 03:10:59)
    '''
    if value.startswith('datetime(') and value.endswith(')'):
        from datetime import datetime
        value = value[len('datetime('):-1]
        if value == 'now':
            value = datetime.now()
        else:
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%s')
    return value


def parse_queryset_options(string):
    '''
    >>> parse_queryset_options('order_by="-created,-pub_date",title__exact="Hello world!",pub_date__lte=datetime(now)')
    [['order_by', '-created'], ['title__exact', 'Hello world!'], ['pub_date__lte', datetime.now()]
    '''
    options = []
    reset, finish = True, False
    open_token = None
    key, value = '', ''
    i = -1
    while True:
        i += 1
        try:
            s = string[i]
        except IndexError:
            reset = True
            finish = True
        if reset:
            if key:
                value = parse_queryset_option_value(value)
                options.append([key, value])
            mode = 'key'
            key, value = '', ''
            reset = False
            if finish:
                break
        if mode == 'key':
            if s == '=':
                if not key:
                    raise ValidationError
                mode = 'value'
                continue
            if s == ',':
                reset = True
                mode = 'key'
            else:
                key += s
        if mode == 'value':
            if not open_token and s == ',':
                reset = True
                continue
            if not open_token and s in ["'", '"']:
                open_token = s
                continue
#            if s == open_token and not masked(open_token, i, s):
            if s == open_token:
                open_token = None
                reset = True
                continue
            value += s
    return options


def apply_queryset_options(queryset, options, callbacks=None):
    if callbacks is None:
        callbacks = {}
    for key, value in options:
        if key in callbacks:
            queryset = callbacks[key](queryset, value)
        elif key in QUERYSET_OPTIONS_CALLBACK:
            queryset = QUERYSET_OPTIONS_CALLBACK[key](queryset, value)
        else:
            if value.startswith('-'):
                queryset = queryset.exclude(**{key: value[:-1]})
            else:
                queryset = queryset.filter(**{key: value})
    return queryset


class GetModelsNode(template.Node):
    def __init__(self, as_value, queryset):
        self.as_value = as_value
        self.queryset = queryset

    def render(self, context):
        context[self.as_value] = self.queryset
        return ''


def get_models(queryset, queryset_options=None):
    QUERYSET = queryset
    def func(parser, token):
        '''
        Example:
            {% get_models as object_list with order_by="-created" %}
        '''
        try:
            tokens = token.contents.split(None, 4)
        except ValueError:
            raise template.TemplateSyntaxError(u'%r tag requires two or four arguments.' % token.contents.split()[0])
        if len(tokens) == 3:
            tokens += [None, None]
        tag_name, as_, as_value, with_, options = tokens
        if as_ != 'as':
            raise template.TemplateSyntaxError(u'%r\'s second argument must be "as".' % tag_name)
        queryset = QUERYSET
        if options is not None:
            options = parse_queryset_options(options)
            queryset = apply_queryset_options(queryset, options, queryset_options)
        if with_ is not None and with_ != 'with':
            raise template.TemplateSyntaxError(u'%r\'s fourth argument must be "with".' % tag_name)
        return GetModelsNode(as_value, queryset)
    return func
