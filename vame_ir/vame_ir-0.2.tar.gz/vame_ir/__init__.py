from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy import engine_from_config
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.security import authenticated_userid
from pyramid.authorization import ACLAuthorizationPolicy


from .models import (
    DBSession,
    Base,
    )
from .security import groupfinder

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    authn_policy = AuthTktAuthenticationPolicy('fguia9yfods', callback=groupfinder, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(settings=settings, root_factory='.security.RootFactory')
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.include('pyramid_chameleon')
    config.include('pyramid_mako')
    config.include('pyramid_tm')

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')

    config.add_route('course_add', '/add/course')
    config.add_route('question_add', '/add/question')
    config.add_route('question_group_add', '/add/question_group')

    config.add_route('course_list','/course/')
    config.add_route('course_page','/course/{course_title}')

    config.add_route('exam_list','/exam')
    config.add_route('exam_page','/exam/{exam_id}')

    config.add_route('certificate','/certificate/{exam_id}')


    config.add_route('quiz_start','/quiz/{quiz_id}')
    config.add_route('quiz_finish','/quiz/{quiz_id}/finish')
    config.add_route('quiz_result','/quiz/{quiz_id}/result')
    config.add_route('quiz_question','/quiz/{quiz_id}/{question_id}')

    config.add_route('login','/login')
    config.add_route('logout','/logout')
    config.add_route('signup','/signup')
    config.add_route('profile', '/profile/{login_name}')
    config.add_route('payment', '/payment')
    config.add_route('score_exam_list', '/score')
    config.add_route('score_exam_page', '/score/{exam_id}')
    # config.add_notfound_view(append_slash=True)

    config.scan()

    return config.make_wsgi_app()

mysettings = {'pyramid.default_locale_name': 'fa', 'pyramid.debug_authorization': 'false', 'pyramid.debug_routematch': 'false',
            'pyramid.reload_templates': 'false', 'sqlalchemy.url': 'mysql+pymysql://root:1@localhost/alchemy?charset=utf8&use_unicode=1',
            'pyramid.debug_notfound': 'false'}
