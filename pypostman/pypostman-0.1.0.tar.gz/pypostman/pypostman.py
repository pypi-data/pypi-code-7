# -*- coding: utf-8 -*-
#!/usr/bin/python
import smtplib
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from cStringIO import StringIO
from email import Charset
from email.generator import Generator
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import simplejson

FROMADDR = 'from@example.com'
RECIPIENT = 'to@gmail.com'
SUBJECT = u"Hello!"

EMAIL_BODY = """
Nombre= %(name)s
Teléfono= %(phone)s
Email= %(email)s
Comentarios= %(comments)s
"""

USERNAME = ''
PASSWORD = ''

PORT_NUMBER = 8080


class MailHandler(BaseHTTPRequestHandler):
    def _assemble_message(self, message):
        subject = SUBJECT
        recipient = RECIPIENT
        from_address = FROMADDR

        text = message.decode('utf-8')
        html = u'<html><body>%s</body></html>' % text

        Charset.add_charset('utf-8', Charset.QP, Charset.QP, 'utf-8')

        multipart = MIMEMultipart('alternative')

        multipart['Subject'] = Header(subject.encode('utf-8'), 'UTF-8').encode()
        multipart['To'] = Header(recipient.encode('utf-8'), 'UTF-8').encode()
        multipart['From'] = Header(from_address.encode('utf-8'), 'UTF-8').encode()

        htmlpart = MIMEText(html.encode('utf-8'), 'html', 'UTF-8')
        multipart.attach(htmlpart)
        textpart = MIMEText(text.encode('utf-8'), 'plain', 'UTF-8')
        multipart.attach(textpart)

        io = StringIO()
        g = Generator(io, False) # second argument means "should I mangle From?"
        g.flatten(multipart)

        return io.getvalue()

    def do_POST(self):
        try:
            content_len = int(self.headers.getheader('content-length', 0))
            post_body = self.rfile.read(content_len)
            content = simplejson.loads(post_body)
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.starttls()
            server.login(USERNAME,PASSWORD)
            msg = EMAIL_BODY % content
            #safe_msg = msg.encode("ascii", "replace")
            #server.sendmail(fromaddr, toaddrs, safe_msg)
            encoded_message = self._assemble_message(msg)
            #server.sendmail(fromaddr, toaddrs, safe_msg)
            server.sendmail(FROMADDR, RECIPIENT, encoded_message)
            server.quit()
            self.send_response(200)
        except Exception, e:
            print e
            self.send_response(500)
        finally:
            self.end_headers()
        return

try:
    #Create a web server and define the handler to manage the
    #incoming request
    server = HTTPServer(('', PORT_NUMBER), MailHandler)
    print 'Started httpserver on port ' , PORT_NUMBER
    #Wait forever for incoming http requests
    server.serve_forever()

except KeyboardInterrupt:
    print '^C received, shutting down the web server'
    server.socket.close()

