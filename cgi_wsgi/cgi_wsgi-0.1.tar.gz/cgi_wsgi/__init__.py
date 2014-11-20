def info():
    print('cgi-wsgi')


class CGIContext:
    def __init__(self):
        self.headers = {}
        self.body = []
        self.writing_headers = True

    def append_body(self, lineOrLinesOrNil):
        # print 'BODY: %s' % lineOrLinesOrNil
        self.body.append(lineOrLinesOrNil or '')

    def add_header(self, line):
        key, value = line.split(': ', 1)
        # print 'HEAD: %s : %s' % (key,value)
        self.headers[key] = value

    def writeln(self, line=''):
        for line in line.split("\n"):
            self.process_line(line)

    def process_line(self, line):
        if not self.writing_headers:
            self.append_body(line)
        elif not line:
            self.writing_headers = False
        else:
            self.add_header(line)

class CGIApp:
    def __call__(self, environ, start_response):
        status = '200 OK'
        context = CGIContext()
        self.response(environ, context.writeln)
        # print context.headers
        start_response(status, context.headers.items())
        return context.body

    def response(self, environ, writeln):
        writeln('Content-type: text/plain')
        writeln()
        writeln("""You should really implement your own response.

e.g.

class %s(cgi_wsgi.CGIApp):

    def response(self, environ, writeln):
        writeln('Content-type: text/html')
        writeln()
        writeln('<!DOCTYPE html>')
        writeln('<p>Some response required</p>')

        """ % self.__class__.__name__
        )