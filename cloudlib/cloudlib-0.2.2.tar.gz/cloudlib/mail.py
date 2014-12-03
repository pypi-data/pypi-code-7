# =============================================================================
# Copyright [2014] [Kevin Carter]
# License Information :
# This software has no warranty, it is provided 'as is'. It is your
# responsibility to validate the behavior of the routines and its accuracy
# using the code provided. Consult the GNU General Public license for further
# details (see GNU General Public License).
# http://www.gnu.org/licenses/gpl.html
# =============================================================================
"""Example Usage:
>>> from cloudlib import mail
>>> config_dict = {
...     'mail_url': 'smtp.google.com',
...     'mail_port': 587,
...     'mail_key': '/etc/ssl/mail.key',
...     'mail_cert': '/etc/ssl/mail.crt',
...     'mail_username': 'UserName',
...     'mail_password': 'PassW0rd'
... }
>>> message = mail.Mailer(
...     config=config_dict,
... )
>>> message.send(
...     send_to='user@somedomain.sufix',
...     from_who='user@someotherdomain.sufix',
...     message='the quick brown fox jumped over the fence',
...     subject='Something really interesting'
... )
"""

import smtplib
from email.mime import text

import cloudlib

from cloudlib import logger


class Mailer(object):

    def __init__(self, config, log_name=__name__):
        """General purpose Email Message Sender.

        This module is used to send messages based on some set values.

        :param config: ``dict``
        :param log_name: ``str`` This is used to log against an existing log
                                 handler.
        """
        # Set logger
        self.log = logger.getLogger(log_name)

        # Set the default args
        if not isinstance(config, dict):
            msg = 'No Configuration Provided'
            self.log.fatal(msg)
            raise cloudlib.MissingConfig(msg)
        else:
            self.config = config

        # Set SMTP
        mail_url = self.config.get('mail_url')
        mail_port = self.config.get('mail_port')
        if mail_port is None:
            raise cloudlib.MissingConfigValue('Missing "mail_port" in config')
        elif mail_url is None:
            raise cloudlib.MissingConfigValue('Missing "mail_url" in config')
        else:
            self.smtp = smtplib.SMTP(mail_url, mail_port)

        # enable Debug
        if self.config.get('debug', False) is True:
            self.smtp.set_debuglevel(True)

        key = self.config.get('mail_key')
        cert = self.config.get('mail_cert')
        if key is not None and cert is not None:
            self.smtp.starttls(key, cert)
        else:
            self.smtp.starttls()

        username = self.config.get('mail_username')
        password = self.config.get('mail_password')
        if username is not None and password is not None:
            self.smtp.login(username, password)

    def send(self, send_to, from_who, subject, message, reply_to=None):
        """Send Email.

        To use this module pass in a message, send_to, from_who, and subject.

        :param send_to: ``str``
        :param from_who: ``str``
        :param subject: ``str``
        :param message: ``str``
        :param reply_to: ``str``
        """
        # Set the reply to address if it's None
        if reply_to is None:
            reply_to = from_who

        try:
            encoded_message = message.encode('utf8')
            em_msg = text.MIMEText(encoded_message, 'plain', None)
            em_msg["Subject"] = subject
            em_msg["From"] = from_who
            em_msg["To"] = send_to
            em_msg["Reply-To"] = reply_to

            # Send Customer Messages
            built_message = em_msg.as_string()

            self.smtp.sendmail(
                from_addr=em_msg["From"],
                to_addrs=em_msg["To"],
                msg=built_message
            )
        except Exception as exp:
            msg = 'Failed to send message due to "%s"' % exp
            self.log.error(msg)
            raise cloudlib.MessageFailure(msg)
        else:
            self.log.debug(message)
        finally:
            self.smtp.quit()
