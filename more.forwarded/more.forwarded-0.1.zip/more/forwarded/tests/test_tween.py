import morepath
from webtest import TestApp as Client
from more.forwarded import ForwardedApp
import more.forwarded

def test_forwarded_app():
    config = morepath.setup()

    config.scan(more.forwarded)

    class App(ForwardedApp):
        testing_config = config

    @App.path(path='foo')
    class Root(object):
        pass

    @App.view(model=Root)
    def root_default(self, request):
        return request.link(self)

    config.commit()

    c = Client(App())

    response = c.get('/foo',
                     headers={'Forwarded': 'host=www.example.com'})

    assert response.body == b'http://www.example.com/foo'
