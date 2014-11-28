from django.contrib.sites.models import Site

from banzai.mail import MailPackage
from banzai.api import BanzaiAPI
from banzai.settings import BANZAI_API_FAST_ADD_METHOD_RECIPIENTS_MAX_COUNT


def send_mail(subject, message, from_email, recipient_list, **kwargs):
    current_site = Site.objects.get_current()

    send_at = kwargs.pop('send_at', None)
    headers = kwargs.pop('headers', [])
    attach_images = kwargs.pop('attach_images', u'0')
    description = kwargs.pop('description', u'')

    mail_package = MailPackage(from_email, current_site.name, subject, message,
                               send_at, headers, attach_images, description)
    mail_package.add_recipients(recipient_list)
    package = mail_package.save()

    banzai_api_obj = BanzaiAPI(package)
    if package.emails_all < BANZAI_API_FAST_ADD_METHOD_RECIPIENTS_MAX_COUNT:
        package = banzai_api_obj.fast_add()
        sended_emails = package.emails_correct
    else:
        package = banzai_api_obj.add()
        sended_emails = package.emails_all

    return sended_emails
