# pyramid
from pyramid.exceptions import NotFound
from pyramid.response import Response
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config

# pyramid_debugtoolbar
import pyramid_debugtoolbar
from pyramid_debugtoolbar.views import valid_host, valid_request
from pyramid_debugtoolbar.utils import find_request_history
from pyramid_debugtoolbar.panels.sqla import SQLADebugPanel

# stdlib
import csv
import logging
import time
import StringIO

# ==============================================================================


def includeme(config):
    """
    was having some trouble trying to handle this in the config correctly

    could not integrate it in a way that the `find_request_history` function would work

    these 2 other forms work with the code below:

    Method B:
        import pyramid
        registry = None
        for i in pyramid.config.global_registries:
            if i.__name__ == 'pyramid_debugtoolbar':
                registry = i
                break
        if not registry:
            raise ValueError("can't do this")
        configurator = pyramid.config.Configurator(registry=registry)
        config.add_route('_debug_toolbar_api.request.sqla_csv', '/_debug_toolbar_api/{request_id}/sqla.csv')
        config.scan('pyramid_debugtoolbar_sqla_csv')
        config.commit()

    Method C:
        config.add_route('_debug_toolbar_api.request.sqla_csv', '/_debug_toolbar_api/{request_id}/sqla.csv')
        config.scan('pyramid_debugtoolbar_sqla_csv')
        config.commit()

    """
    altconfig = config.with_package('pyramid_debugtoolbar')
    altconfig.add_route('_debug_toolbar_api.request.sqla_csv', '/_debug_toolbar_api/{request_id}/sqla.csv')
    altconfig.scan('pyramid_debugtoolbar_sqla_csv')
    altconfig.commit()


# ==============================================================================


@view_config(
    route_name='_debug_toolbar_api.request.sqla_csv',
    permission=NO_PERMISSION_REQUIRED,
    custom_predicates=(valid_host, valid_request)
)
def request_sqla_csv(request):

    # we don't use the debugtoolbar method `find_request_history`
    # why? because our request.registry already has `request_history`
    # it doesn't have `parent_registry`
    history = request.registry.request_history

    try:
        last_request_pair = history.last(1)[0]
    except IndexError:
        last_request_pair = None
        last_request_id = None
    else:
        last_request_id = last_request_pair[0]

    request_id = request.matchdict.get('request_id', last_request_id)
    toolbar = history.get(request_id, None)

    if not toolbar:
        raise NotFound

    sqla_panel = None
    for panel in toolbar.panels:
        if isinstance(panel, pyramid_debugtoolbar.panels.sqla.SQLADebugPanel):
            sqla_panel = panel
    if not sqla_panel:
        raise NotFound

    csvfile = StringIO.StringIO()
    csvwriter = csv.writer(csvfile)
    for query in sqla_panel.data['queries']:
        csvwriter.writerow((query['duration'], query['raw_sql'], pyramid_debugtoolbar.panels.sqla.text(query['parameters'])))
    csvfile.seek(0)
    as_csv = Response(
        content_type = 'text/csv',
        body_file = csvfile,
        status = 200,
    )
    as_csv.headers['Content-Disposition'] = str('attachment; filename= sql-%s.csv' % request_id)
    return as_csv
