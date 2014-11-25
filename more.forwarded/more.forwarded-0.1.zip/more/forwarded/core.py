import morepath
from .forwarded import handler_factory


class ForwardedApp(morepath.App):
    pass


@ForwardedApp.tween_factory(over=morepath.EXCVIEW)
def forwarded_tween_factory(app, handler):
    return handler_factory(handler)
