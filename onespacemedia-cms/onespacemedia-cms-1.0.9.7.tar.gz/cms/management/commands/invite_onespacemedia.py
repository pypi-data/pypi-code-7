from django import template
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse


class Command(BaseCommand):
    help = "Invites all Onespacemedia members to the CMS"

    def handle(self, *args, **options):
        """ Invites all Onespacemedia members to the CMS """


        """Sends an invitation email to the given user."""
        confirmation_url = reverse(
            "{admin_site}:auth_user_invite_confirm".format(
                admin_site=self.admin_site.name,
            ), kwargs={
                "uidb36": int_to_base36(user.id),
                "token": default_token_generator.make_token(user),
            }
        )
        send_mail(
            "{prefix}You have been invited to create an account".format(
                prefix=settings.EMAIL_SUBJECT_PREFIX,
            ),
            template.loader.render_to_string(
                "admin/auth/user/invite_email.txt", {
                    "user": user,
                    "confirmation_url": confirmation_url,
                    "sender": request.user,
                }),
            settings.DEFAULT_FROM_EMAIL,
            ("{first_name} {last_name} <{email}>".format(
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
            ),),
        )
