
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from contextlib import contextmanager as ctx

from html import HtmlRenderer


class Htmail(object):
    def __init__(self, sender, sendee, smtp_server):
        self._me = sender
        self._you = sendee if isinstance(sendee, basestring) else ';'.join(sendee)
        self._serv = smtp_server

    def _send_message(self, msg):
        s = smtplib.SMTP(self._serv)
        s.sendmail(self._me, self._you, msg.as_string())
        s.quit()

    def _get_message(self, subject):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self._me
        msg['To'] = self._you
        return msg

    @ctx
    def send(self, subject):
        msg = self._get_message(subject)
        mail = HtmlRenderer()
        yield mail
        html = MIMEText(str(mail), 'html')
        msg.attach(html)
        self._send_message(msg)