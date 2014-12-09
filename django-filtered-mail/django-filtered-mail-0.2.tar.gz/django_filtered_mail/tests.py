import re

from django.test import TestCase
from django.core.mail import EmailMessage

from django_filtered_mail.mail import filter_recipients, filter_message


class StagingMailTestCase(TestCase):

    def test_filter(self):
        allowed = (
            re.compile(r'^.*@dreamsolution.nl$'),
            re.compile(r'^test-dreamsolution@gmail.com$'),
        )

        recipients = (
            'test@dreamsolution.nl',
            'test-dreamsolution@gmail.com',
            'example@example.com',
            'Some one <some-one@dreamsolution.nl>',
            'dreamsolution.nl@example.com',
        )

        recipients = filter_recipients(recipients, allowed, 'UTF-8')
        self.assertEqual(recipients, [
            'test@dreamsolution.nl',
            'test-dreamsolution@gmail.com',
            'Some one <some-one@dreamsolution.nl>',
        ])

    def test_message(self):
        allowed = [re.compile(r'^.*@dreamsolution.nl$')]

        # test valid address
        email = EmailMessage('Subject', 'Content', 'bounce@example.com',
            ['to@dreamsolution.nl'])
        email = filter_message(email, allowed)
        self.assertEqual(email.to, ['to@dreamsolution.nl'])

        # test invalid address
        email = EmailMessage('Subject', 'Content', 'bounce@example.com',
            ['test@gmail.com'])
        email = filter_message(email, allowed)
        self.assertEqual(email.to, [])

        # test one valid and one invalid 'To' address
        email = EmailMessage('Subject', 'Content', 'bounce@example.com',
            ['test@gmail.com', 'to@dreamsolution.nl'])
        email = filter_message(email, allowed)
        self.assertEqual(email.to, ['to@dreamsolution.nl'])

        # test multiple valid 'To' addresses
        email = EmailMessage('Subject', 'Content', 'bounce@example.com',
            ['test@dreamsolution.nl', 'to@dreamsolution.nl'])
        email = filter_message(email, allowed)
        self.assertEqual(email.to, ['test@dreamsolution.nl',
            'to@dreamsolution.nl'])

        # test 'Cc'
        email = EmailMessage('Subject', 'Content', 'bounce@example.com',
            ['test@gmail.com'], cc=['cc@dreamsolution.nl'])
        email = filter_message(email, allowed)
        self.assertEqual(email.cc, ['cc@dreamsolution.nl'])
        self.assertEqual(email.recipients(), ['cc@dreamsolution.nl'])

        # test 'Bcc'
        email = EmailMessage('Subject', 'Content', 'bounce@example.com',
            ['test@gmail.com', 'to@dreamsolution.nl'],
            bcc=['bcc@dreamsolution.nl'])
        email = filter_message(email, allowed)
        self.assertEqual(email.bcc, ['bcc@dreamsolution.nl'])
        self.assertEqual(email.recipients(), [
            'to@dreamsolution.nl', 'bcc@dreamsolution.nl'])

    # Testing the backend is harder, one needs a (local) SMTP server
    #def test_backend(self):
    #    connection = EmailBackend()
    #    connection.set_allowed_recipients([r'^.*@dreamsolution.nl$'])
