from django.template.loader import render_to_string
from email.mime.image import MIMEImage
import mimetypes
from django.core.mail import EmailMultiAlternatives


def send_mail(subject, text_content, from_email, to, html_content=None, attachments=[], cc=[], bcc=[]):
    """
    This function sends mail using EmailMultiAlternatives and attachs all attachments
    passed as parameters
    """
    msg = EmailMultiAlternatives(subject, text_content, from_email, to, cc=cc, bcc=bcc)
    if html_content:
        msg.attach_alternative(html_content, "text/html")
    if attachments:
        for att in attachments:
            if att:

                mimetype = mimetypes.guess_type(att)[0]
                if str(mimetype) in ('image/jpeg', 'image/pjpeg', 'image/png', 'image/gif'):
                    try:
                        with open(att, 'r') as f:
                            email_embed_image(msg, att, f.read())
                    except Exception, e:
                        print e
                else:
                    msg.attach_file(att)
    return msg.send()


def send_rendered_mail(subject, template_name, context_dict, from_email, to, attachments=[], cc=[], bcc=[]):
    """
    It sends mail after rendering html content and normal text using two different template (.html, .txt) with
    the same name.

    :param subject:
    :param template_name: without file extension
    :param context_dict:
    :param from_email:
    :param to:
    :param attachments:
    """
    rendered = render_to_string(u"{}.html".format(template_name), context_dict)
    text_content = render_to_string(u"{}.txt".format(template_name), context_dict)
    return send_mail(subject, text_content, from_email, to, rendered, attachments, cc=cc, bcc=bcc)


def email_embed_image(email, img_content_id, img_data):
    """
    email is a django.core.mail.EmailMessage object
    """
    img = MIMEImage(img_data)
    img.add_header('Content-ID', '<%s>' % img_content_id)
    img.add_header('Content-Disposition', 'inline')
    email.attach(img)
