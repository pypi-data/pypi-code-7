""" Configures the email sender settings for all or just the given plone
site.

WARNING: Does not take subsites into consideration!

Run as follows:

bin/instance run <path to seantis.plonetools>
/seantis/plonetools/scripts/configure-email.py
smtp-server smtp-server-port [esmpt-username | ''] ] [esmpt-password | '']
sender-name sender-address [site]

Examples:

Setup smtp for all sites
bin/instance run <path>/configure-email.py mail.example.org 25 user@example.org
password Sender-Name user@example.org

Setup sendmail for 'my-site'
bin/instance run <path>/configure-email.py localhost 25 '' '' Sender-Name
user@example.org my-site

"""


import logging
import sys
import transaction

from plone.app.controlpanel.mail import IMailSchema
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component.hooks import setSite

log = logging.getLogger('seantis.plonetools')


def main(app):
    server = sys.argv[3]
    port = sys.argv[4]
    username = sys.argv[5]
    password = sys.argv[6]
    name = sys.argv[7]
    sender = sys.argv[8]

    if len(sys.argv) > 9:
        site = sys.argv[9]
    else:
        site = None

    sites = get_sites(app, site)
    for site in sites:
        log.info("Configuring mail for plone-site '{}'".format(site))
        configure_email(site, server, port, username, password, name, sender)

    transaction.commit()
    log.info("Done")


def get_sites(app, site):
    sites = []

    for key, item in app.items():
        if not IPloneSiteRoot.providedBy(item):
            continue

        if site is None or site == key:
            sites.append(item)

    return sites


def configure_email(site, server, port, username, password, name, sender):
    setSite(site)  # needs to be set for IMailSchema to work
    mail = IMailSchema(site)

    mail.smtp_host = unicode(server)
    mail.smtp_port = int(port)
    mail.smtp_userid = unicode(username)
    mail.smtp_pass = unicode(password)
    mail.email_from_address = unicode(sender)
    mail.email_from_name = unicode(name)


if 'app' in locals():
    main(locals()['app'])
