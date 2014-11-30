from inspect import getargspec
import collections

from django.core import cache
from django.template import Context, Node, Variable
from django.template.base import TemplateSyntaxError
from django.template.loader import get_template, select_template
from django.utils.functional import curry
from django.utils.itercompat import is_iterable


def configurable_inclusion_tag(register, cache_key=None, cache_time=60):
    """Works like normal inclusion tag but it allows the wrapped function to specify which
    template to use, or to abort althogether and return.

    * first argument must always be 'context'
    * if return value is None, then display nothing
    * otherwise, return value should be a (template_name, context_or_dict)
    """

    def dec(func):
        params, xx, xxx, defaults = getargspec(func)
        if params[0] == 'context':
            params = params[1:]
        else:
            raise TemplateSyntaxError("Must have a first argument of 'context'")

        class InclusionNode(Node):
            def __init__(self, vars_to_resolve):
                self.vars_to_resolve = list(map(Variable, vars_to_resolve))
                self.nodelists = {}

            @staticmethod
            def calculate_cache_key(args):
                if cache_key:
                    if isinstance(cache_key, collections.Callable):
                        return cache_key(*args)
                    else:
                        return cache_key
                return None

            def render(self, context):
                resolved_vars = [var.resolve(context) for var in self.vars_to_resolve]
                args = [context] + resolved_vars
                my_cache_key = self.calculate_cache_key(args)
                if my_cache_key:
                    output = cache.cache.get(my_cache_key)
                    if output:
                        return output
                returnval = func(*args)
                if not returnval:
                    return ""
                (file_name, dict_) = returnval

                if file_name not in self.nodelists:
                    if not isinstance(file_name, str) and is_iterable(file_name):
                        t = select_template(file_name)
                    else:
                        t = get_template(file_name)
                    self.nodelists[file_name] = t.nodelist
                new_context = Context(dict_)
                # Copy across the CSRF token, if present, because inclusion
                # tags are often used for forms, and we need instructions
                # for using CSRF protection to be as simple as possible.
                csrf_token = context.get('csrf_token', None)
                if csrf_token is not None:
                    new_context['csrf_token'] = csrf_token
                output = self.nodelists[file_name].render(new_context)
                if my_cache_key:
                    cache.cache.set(my_cache_key, output, cache_time)
                return output

        compile_func = curry(old_generic_tag_compiler, params, defaults,
                             getattr(func, "_decorated_function", func).__name__, InclusionNode)
        compile_func.__doc__ = func.__doc__
        register.tag(getattr(func, "_decorated_function", func).__name__, compile_func)
        return func

    return dec


# noinspection PyUnusedLocal
def old_generic_tag_compiler(params, defaults, name, node_class, parser, token):
    """Returns a template.Node subclass."""
    bits = token.split_contents()[1:]
    bmax = len(params)
    def_len = defaults and len(defaults) or 0
    bmin = bmax - def_len
    if len(bits) < bmin or len(bits) > bmax:
        if bmin == bmax:
            message = "%s takes %s arguments" % (name, bmin)
        else:
            message = "%s takes between %s and %s arguments" % (name, bmin, bmax)
        raise TemplateSyntaxError(message)
    return node_class(bits)