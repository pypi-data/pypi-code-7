# encoding: utf-8
from copy import copy
from functools import wraps

from mock import Mock
from flea import Agent
import pytest
import tms

from fresco import FrescoApp, GET, POST, Response
from fresco.exceptions import NotFound
from fresco.compat import ustring_type
from fresco.core import urlfor
from fresco.routing import (
    Route, DelegateRoute, RouteCollection, routefor, RouteTraversal,
    RouteNotFound)
from . import fixtures


class TestMethodDispatch(object):

    def test_route_is_dispatched_to_correct_method(self):

        getview = Mock(return_value=Response(content_type='text/plain'))
        postview = Mock(return_value=Response(content_type='text/plain'))
        app = FrescoApp()
        app.route('/', GET, getview)
        app.route('/', POST, postview)

        Agent(app).get('/')
        assert getview.call_count == 1
        assert postview.call_count == 0

        Agent(app).post('/')
        assert getview.call_count == 1
        assert postview.call_count == 1


class TestRouteViewFilters(object):

    def exclaim(self, response):
        return response.replace(content=[''.join(response.content) + '!'])

    def ask(self, response):
        return response.replace(content=[''.join(response.content) + '?'])

    def test_filter_is_applied(self):
        views = fixtures.CBV('test')
        app = FrescoApp()
        app.route('/', GET, views.index_html).filter(self.ask)
        with app.requestcontext('/'):
            assert app.view().content == ['test?']

    def test_it_applies_multiple_filters_in_order(self):
        app = FrescoApp()
        views = fixtures.CBV('test')
        app.route('/', GET, views.index_html).filter(self.ask, self.exclaim)
        with app.requestcontext('/'):
            assert app.view().content == ['test?!']

    def test_it_applies_chained_filter_calls_in_order(self):
        app = FrescoApp()
        views = fixtures.CBV('test')
        app.route('/', GET, views.index_html)\
                .filter(self.ask).filter(self.exclaim)
        with app.requestcontext('/'):
            assert app.view().content == ['test?!']


class TestRouteDecorators(object):

    def exclaim(self, func):
        @wraps(func)
        def exclaim(*args, **kwargs):
            response = func(*args, **kwargs)
            return response.replace(content=[''.join(response.content) + '!'])
        return exclaim

    def test_decorator_is_applied(self):

        views = fixtures.CBV('test')

        app = FrescoApp()
        app.route('/decorated', GET, views.index_html,
                  decorators=[self.exclaim])
        app.route('/plain', GET, views.index_html)

        with app.requestcontext('/decorated'):
            assert app.view().content == ['test!']

        with app.requestcontext('/plain'):
            assert app.view().content == ['test']

    def test_decorator_is_applied_with_wrap_method(self):

        views = fixtures.CBV('test')

        app = FrescoApp()
        app.route('/decorated', GET, views.index_html).wrap(self.exclaim)
        app.route('/plain', GET, views.index_html)

        with app.requestcontext('/decorated'):
            assert app.view().content == ['test!']

        with app.requestcontext('/plain'):
            assert app.view().content == ['test']

    def test_decorator_works_with_urlfor(self):

        views = fixtures.CBV('test')
        app = FrescoApp()
        app.route('/decorated', GET, views.index_html,
                  decorators=[self.exclaim])
        with app.requestcontext():
            assert urlfor(views.index_html, _app=app) == \
                'http://localhost/decorated'

    def test_using_wraps_with_viewspec_doesnt_raise_AttributeError(self):

        def decorator(func):
            @wraps(func)
            def decorator(*args, **kwargs):
                return func(*args, **kwargs)
            return decorator

        class Views(object):
            __routes__ = Route('/',
                               GET, 'index_html', decorators=[decorator]),

            def index_html(self):
                return Response(['hello'])

        app = FrescoApp()
        app.include('/', Views())


class TestPredicates(object):

    def test_predicate_match(self):

        def v1():
            return Response(['x'])

        def v2():
            return Response(['y'])

        app = FrescoApp()
        app.route('/', GET, v1, predicate=lambda request: 'x' in request.query)
        app.route('/', GET, v2, predicate=lambda request: 'y' in request.query)

        t = Agent(app)
        assert t.get('/?x=1', check_status=False).body == 'x'
        assert t.get('/?y=1', check_status=False).body == 'y'
        assert t.get('/', check_status=False).response.status_code == 404


class TestRouteNames(object):

    def test_name_present_in_route_keys(self):
        r = Route('/', GET, None, name='foo')
        assert 'foo' in list(r.route_keys())

    def test_name_with_other_kwargs(self):
        r = Route('/', GET, None, name='foo', x='bar')
        assert 'foo' in list(r.route_keys())

    def test_name_cannot_contain_colon(self):
        with pytest.raises(ValueError):
            Route('/', GET, None, name='foo:bar')


class TestRouteCollection(object):

    def test_get_routes_matches_on_method(self):

        r_get = Route('/', GET, None)
        r_post = Route('/', POST, None)

        rc = RouteCollection([r_post, r_get])

        assert [r.route for r in rc.get_routes('/', GET)] == [r_get]
        assert [r.route for r in rc.get_routes('/', POST)] == [r_post]

    def test_get_routes_matches_on_path(self):

        r1 = Route('/1', GET, None)
        r2 = Route('/2', GET, None)

        rc = RouteCollection([r1, r2])

        assert [r.route for r in rc.get_routes('/1', GET)] == [r1]
        assert [r.route for r in rc.get_routes('/2', GET)] == [r2]

    def test_get_routes_can_match_all_methods(self):

        r1 = Route('/1', GET, None)
        r2 = Route('/1', POST, None)

        rc = RouteCollection([r1, r2])
        assert [r.route for r in rc.get_routes('/1', None)] == [r1, r2]

    def test_route_returns_traversal_information_on_nested_routes(self):

        a = RouteCollection()
        b = RouteCollection()

        a.route('/harvey', GET, lambda: None)
        b.route('/harvey', GET, lambda: None)

        a.delegate('/rabbit', b)
        b.delegate('/hole', a)

        r = next(a.get_routes('/rabbit/hole/rabbit/harvey', None))
        assert r.collections_traversed == [(a, ''),
                                           (b, '/rabbit'),
                                           (a, '/rabbit/hole'),
                                           (b, '/rabbit/hole/rabbit')]

    def test_pathfor_works_with_positional_args(self):
        view = Mock()
        rc = RouteCollection([Route('/<:str>', GET, view)])
        assert rc.pathfor(view, 'x') == '/x'

    def test_replace_raises_route_not_found(self):
        a = RouteCollection()
        view = Mock()
        a.route('/harvey', GET, view, name='harvey')
        with pytest.raises(RouteNotFound):
            a.replace('rabbit', None)

    def test_replace_selects_routes_by_name(self):
        a = RouteCollection()
        oldroute = Route('/', GET, Mock(), name='harvey')
        newroute = Route('/', GET, Mock())
        a.add_route(oldroute)
        a.replace('harvey', newroute)
        assert a.__routes__ == [newroute]

    def test_replace_selects_routes_by_view(self):
        a = RouteCollection()
        view = Mock()
        oldroute = Route('/', GET, view)
        newroute = Route('/', GET, Mock())
        a.add_route(oldroute)
        a.replace(view, newroute)
        assert a.__routes__ == [newroute]

    def test_can_add_a_list_to_a_routecollection(self):
        r1 = Route('/', GET, Mock())
        r2 = Route('/', GET, Mock())
        assert (RouteCollection([r1]) + [r2]).__routes__ == [r1, r2]

    def test_can_add_routecollections(self):
        r1 = Route('/', GET, Mock())
        r2 = Route('/', GET, Mock())
        assert (RouteCollection([r1]) + RouteCollection([r2])).__routes__ == \
                [r1, r2]

    def test_routecollections_can_be_used_in_classes(self):
        class MyViews(object):
            __routes__ = RouteCollection([
                Route('/', GET, 'view')])

            def view(self):
                pass

        v = MyViews()
        app = FrescoApp()
        app.include('/', v)
        assert [r.route.getview()
                for r in app.get_routes('/', GET)] == [v.view]

    def test_routecollections_in_classes_can_be_manipulated(self):
        class MyViews(object):
            __routes__ = RouteCollection([
                Route('/', GET, 'view')])

            def view(self):
                pass

        class MyOtherViews(MyViews):
            __routes__ = copy(MyViews.__routes__)
            __routes__.replace('view', Route('/', GET, 'another_view'))

            def another_view(self):
                pass

        v = MyOtherViews()
        app = FrescoApp()
        app.include('/', v)
        assert [r.route.getview()
                for r in app.get_routes('/', GET)] == [v.another_view]


class TestRoutefor(object):

    def test_routefor_with_view_function(self):

        def view():
            return Response(['ok'])

        app = FrescoApp()
        route = app.route('/foo', GET, view)

        with app.requestcontext():
            assert routefor(view) == route

    def test_routefor_with_string(self):
        app = FrescoApp()
        route = app.route('/myviewfunc', GET, fixtures.module_level_function)
        with app.requestcontext():
            assert routefor('fresco.tests.fixtures.module_level_function') == \
                route

    def test_routefor_generates_first_route(self):

        myviewfunc = lambda req: Response([])
        app = FrescoApp()
        r1 = app.route('/1', GET, myviewfunc)
        app.route('/2', GET, myviewfunc)
        with app.requestcontext():
            assert routefor(myviewfunc) == r1


class TestDelegatedRoutes(object):

    def test_dispatch_to_delegated_route(self):

        def hello():
            return Response(['hello'])

        inner = FrescoApp()
        inner.route('/hello', GET, hello)

        outer = FrescoApp()
        outer.delegate('/say', inner)

        r = Agent(outer).get('/say/hello')
        assert r.body == 'hello'

    def test_url_variables_are_passed(self):

        hello = Mock()

        inner = FrescoApp()
        inner.route('/<i:str>', GET, hello)

        outer = FrescoApp()
        outer.delegate('/<o:str>', inner)

        with outer.requestcontext('/foo/bar'):
            outer.view()
            hello.assert_called_with(i='bar', o='foo')

    def test_delegation_to_dynamic_routes(self):

        result = []

        class MyRoutes(object):
            __routes__ = [Route('/<inner:int>/view', GET, 'view')]

            def __init__(self, **kwargs):
                self.kwargs = kwargs

            def view(self, **kwargs):
                result.append((self, kwargs))

        app = FrescoApp()
        app.delegate('/<outer:str>', MyRoutes, dynamic=True)
        with app.requestcontext('/two/2/view'):
            app.view()
            instance, inner_kwargs = result[0]
            assert inner_kwargs == {'inner': 2}
            assert instance.kwargs == {'outer': 'two'}

    def test_dynamic_routes_are_never_shared(self):

        result = []

        class MyRoutes(object):
            __routes__ = [Route('', GET, 'view')]

            def __init__(self, value):
                self.value = value

            def view(self):
                result.append(self.value)

        app = FrescoApp()
        app.delegate('/<value:str>', MyRoutes, dynamic=True)
        with app.requestcontext('/one'):
            app.view()
            v1 = result.pop()
        with app.requestcontext('/two'):
            app.view()
            v2 = result.pop()
        assert v1 == 'one'
        assert v2 == 'two', v2

    def test_pathfor_with_delegated_route(self):
        inner = FrescoApp()
        inner.route('/<i:str>', GET, lambda: None, name='inner-route')

        outer = FrescoApp()
        outer.delegate('/<o:str>', inner, name='delegation')

        with outer.requestcontext('/foo/bar'):
            assert outer.pathfor('delegation:inner-route',
                                 o='x', i='y') == '/x/y'

    def test_pathfor_with_dynamic_delegated_route(self):

        view = Mock()

        def routecollectionfactory(*args, **kwargs):
            return RouteCollection([Route('/<i:str>', GET, view,
                                          name='inner-route')])

        rc = RouteCollection()
        rc.delegate('/<o:str>', routecollectionfactory,
                    name='delegation', dynamic=True)

        assert rc.pathfor('delegation:inner-route', o='x', i='y') == '/x/y'

    def test_pathfor_with_dynamic_delegated_route_uses_default_args(self):

        view = Mock()

        def routecollectionfactory(factoryarg1, factoryarg2):
            return RouteCollection([Route('/<i:str>', GET, view,
                                          name='inner-route')])

        rc = RouteCollection()
        rc.delegate('/<factoryarg1:str>/<factoryarg2:str>',
                    routecollectionfactory,
                    factoryarg1_default='foo',
                    factoryarg2_default=lambda r: 'bar',
                    name='delegation', dynamic=True)

        assert rc.pathfor('delegation:inner-route', i='y') == '/foo/bar/y'

    def test_urlfor_with_dynamic_delegated_route_and_view_self(self):

        result = []

        class MyRoutes(object):
            __routes__ = [Route('/<inner:int>/view', GET, 'view')]

            def __init__(self, **kwargs):
                self.kwargs = kwargs

            def view(self, **kwargs):
                result.append(urlfor(self.view, inner=3))

        app = FrescoApp()
        app.delegate('/<outer:str>', MyRoutes, dynamic=True)
        with app.requestcontext('/two/2/view'):
            app.view()
            assert result == ['http://localhost/two/3/view']

    def test_urlgeneration_with_dynamic_routes(self):

        class Routable(object):
            __routes__ = [Route('/<b:int>', GET, 'view', name='y')]

            def __init__(self, a):
                pass

            def view(self, b):
                pass

        app = FrescoApp()
        app.delegate('/<a:str>', Routable, dynamic=True, name='x')
        with app.requestcontext('/two/2/view'):
            assert urlfor('x:y', a='a', b=1) == 'http://localhost/a/1'

    def test_delegated_routes_can_be_included(self):

        view = Mock()

        inner = RouteCollection([Route('/baz', GET, view)])
        middle = RouteCollection([DelegateRoute('/bar', inner)])
        outer = FrescoApp()
        outer.include('/foo', middle)
        with outer.requestcontext('/foo/bar/baz'):
            outer.view()
            view.assert_called()

    def test_not_found_is_returned(self):

        def inner():
            raise NotFound()

        outer = FrescoApp()
        outer.delegate('/foo', inner, dynamic=True)
        with outer.requestcontext('/foo/bar/baz'):
            response = outer.view()
            assert response.status_code == 404

    def test_not_found_causes_next_route_to_be_tried(self):

        def inner():
            raise NotFound()
        view = Mock()

        outer = FrescoApp()
        outer.delegate('/foo', inner, dynamic=True)
        outer.route('/foo', view)
        with outer.requestcontext('/foo'):
            outer.view()
            view.assert_called()


class TestConverters(object):

    def test_str_converter_returns_unicode(self):
        from fresco.routing import StrConverter
        s = ustring_type('abc')
        assert isinstance(StrConverter().from_string(s), ustring_type)

    def test_register_coverter_acts_as_decorator(self):
        from fresco.routing import Converter, register_converter

        @register_converter('testconverter')
        class MyConverter(Converter):
            def from_string(self, s):
                return 'bar'

        view = Mock()

        app = FrescoApp()
        app.route('/<:testconverter>', GET, view)
        with app.requestcontext('/foo'):
            app.view()
            assert view.call_args == (('bar',), {}), view.call_args


class TestViewArgs(object):

    def test_it_uses_args(self):
        routes = RouteCollection([Route('/', GET, None, args=(1, 2))])
        assert list(routes.get_routes('/', GET)) == \
                [tms.InstanceOf(RouteTraversal, args=(1, 2))]

    def test_it_uses_view_args(self):
        routes = RouteCollection([Route('/', GET, None, view_args=(1, 2))])
        assert list(routes.get_routes('/', GET)) == \
                [tms.InstanceOf(RouteTraversal, args=(1, 2))]

    def test_it_appends_args_extracted_from_path(self):
        routes = RouteCollection([Route('/<:int>', GET, None,
                                        view_args=(1, 2))])
        assert list(routes.get_routes('/3', GET)) == \
                [tms.InstanceOf(RouteTraversal, args=(1, 2, 3))]


class TestViewKwargs(object):

    def test_it_reads_from_route_kwargs(self):
        routes = RouteCollection([Route('/', GET, None, x=1)])
        assert list(routes.get_routes('/', GET)) == \
                [tms.InstanceOf(RouteTraversal, kwargs={'x': 1})]

    def test_it_reads_from_kwargs(self):
        routes = RouteCollection([Route('/', GET, None, kwargs={'x': 1})])
        assert list(routes.get_routes('/', GET)) == \
                [tms.InstanceOf(RouteTraversal, kwargs={'x': 1})]

    def test_it_reads_from_view_kwargs(self):
        routes = RouteCollection([Route('/', GET, None, view_kwargs={'x': 1})])
        assert list(routes.get_routes('/', GET)) == \
                [tms.InstanceOf(RouteTraversal, kwargs={'x': 1})]


class TestRouteClassIsPluggable(object):

    class CustomRoute(Route):
        pass

    def test_it_defaults_to_Route(self):
        routes = RouteCollection()
        assert routes.route_class is Route

    def test_it_accepts_route_class_arg(self):
        routes = RouteCollection(route_class=self.CustomRoute)
        assert routes.route_class is self.CustomRoute

    def test_it_uses_route_class_in_route_method(self):

        def myview():
            pass

        routes = RouteCollection(route_class=self.CustomRoute)
        routes.route('/', GET, myview)

        assert list(routes.get_routes('/', GET)) == \
                [tms.InstanceOf(RouteTraversal,
                                route=tms.InstanceOf(self.CustomRoute))]

    def test_it_uses_route_class_in_decorator(self):

        routes = RouteCollection(route_class=self.CustomRoute)

        @routes.route('/', GET)
        def myview():
            pass

        assert list(routes.get_routes('/', GET)) == \
                [tms.InstanceOf(RouteTraversal,
                                route=tms.InstanceOf(self.CustomRoute))]

    def test_custom_route_class_survives_include(self):
        routes = RouteCollection(route_class=self.CustomRoute)

        @routes.route('/', GET)
        def myview():
            pass

        routes2 = RouteCollection()
        routes2.include('/incl', routes)

        assert list(routes2.get_routes('/incl/', GET)) == \
                [tms.InstanceOf(RouteTraversal,
                                route=tms.InstanceOf(self.CustomRoute))]
