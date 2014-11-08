"""
dealing with the fault counters and available/abuse/abuse_blocked flags
"""

from optparse import make_option

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.db import transaction

from nsupdate.main.models import Host


ABUSE_MSG = """\
Your host: %(fqdn)s (comment: %(comment)s)

Issue: The abuse flag for your host was set.

Explanation:
The abuse flag usually gets set if your update client sends way too many
updates although your IP address did not change.

Your update client sent %(faults_count)d faulty updates since we last checked.
We have reset the faults counter to 0 now, but we are rejecting updates
for this host until you resolve the issue.

Resolution:
You can easily do this on your own:
1. fix or replace the update client on this host - it must not send
   updates if the IP did not change
2. visit the service web interface and remove the abuse flag for this host

Notes:
- this is usually caused by a misbehaving / faulty update client
  (on your PC / server or router / firewall)
- the dyndns2 standard explicitly states that frequently sending
  nochg updates is considered abuse of the service
- you are using way more resources on the service than really needed
- for Linux and similar OSes, you can use the ddclient software - we
  give copy&paste-ready configuration help for it on our web UI
- if you need something else, use anything that can be considered
  a valid, well-behaved dyndns2-compatible update client
- if you already used such a software and you ran into this problem,
  complain to whoever wrote it about it sending nochg updates
"""


class Command(BaseCommand):
    help = 'deal with the faults counters'

    option_list = BaseCommand.option_list + (
        make_option('--show-server',
                    action='store_true',
                    dest='show_server',
                    default=False,
                    help='show server fault counters',
        ),
        make_option('--show-client',
                    action='store_true',
                    dest='show_client',
                    default=False,
                    help='show client fault counters',
        ),
        make_option('--reset-server',
                    action='store_true',
                    dest='reset_server',
                    default=False,
                    help='reset the server fault counters of all hosts',
        ),
        make_option('--reset-client',
                    action='store_true',
                    dest='reset_client',
                    default=False,
                    help='reset the client fault counters of all hosts',
        ),
        make_option('--reset-abuse',
                    action='store_true',
                    dest='reset_abuse',
                    default=False,
                    help='reset the abuse flag (to False) of all hosts',
        ),
        make_option('--reset-abuse-blocked',
                    action='store_true',
                    dest='reset_abuse_blocked',
                    default=False,
                    help='reset the abuse_blocked flag (to False) of all hosts',
        ),
        make_option('--reset-available',
                    action='store_true',
                    dest='reset_available',
                    default=False,
                    help='reset the available flag (to True) of all hosts',
        ),
        make_option('--flag-abuse',
                    action='store',
                    dest='flag_abuse',
                    default=None,
                    type='int',
                    help='if client faults > N then set abuse flag and reset client faults',
        ),
        make_option('--notify-user',
                    action='store_true',
                    dest='notify_user',
                    default=False,
                    help='notify the user by email when host gets flagged for abuse',
        ),
    )

    def handle(self, *args, **options):
        show_client = options['show_client']
        show_server = options['show_server']
        reset_client = options['reset_client']
        reset_server = options['reset_server']
        reset_available = options['reset_available']
        reset_abuse = options['reset_abuse']
        reset_abuse_blocked = options['reset_abuse_blocked']
        flag_abuse = options['flag_abuse']
        notify_user = options['notify_user']
        with transaction.atomic():
            for h in Host.objects.all():
                if show_client or show_server:
                    output = u""
                    if show_client:
                        output += u"%-6d " % h.client_faults
                    if show_server:
                        output += u"%-6d " % h.server_faults
                    output += u"%s %s\n" % (h.created_by.username, h.get_fqdn(), )
                    self.stdout.write(output)
                if (flag_abuse is not None or reset_client or reset_server or
                    reset_available or reset_abuse or reset_abuse_blocked):
                    if flag_abuse is not None:
                        if h.client_faults > flag_abuse:
                            h.abuse = True
                            faults_count = h.client_faults
                            h.client_faults = 0
                            fqdn = h.get_fqdn()
                            comment = h.comment
                            creator = h.created_by
                            self.stdout.write("setting abuse flag for host %s (created by %s, client faults: %d)\n" % (
                                              fqdn, creator, faults_count))
                            if notify_user:
                                from_addr = None  # will use DEFAULT_FROM_EMAIL
                                to_addr = creator.email
                                subject = "issue with your host %(fqdn)s" % dict(fqdn=fqdn)
                                msg = ABUSE_MSG % dict(fqdn=fqdn, comment=comment, faults_count=faults_count)
                                send_mail(subject, msg, from_addr, [to_addr], fail_silently=True)
                    if reset_client:
                        h.client_faults = 0
                    if reset_server:
                        h.server_faults = 0
                    if reset_available:
                        h.available = True
                    if reset_abuse:
                        h.abuse = False
                    if reset_abuse_blocked:
                        h.abuse_blocked = False
                    h.save()
