from django.conf import settings


USE_CELERY = getattr(settings, 'TRELLO_BROKER_USE_CELERY', False)

RESTRICT_IPS = getattr(settings, 'TRELLO_BROKER_RESTRICT_IPS', False)

# https://confluence.atlassian.com/display/BITBUCKET/What+are+the+Bitbucket+IP+addresses+I+should+use+to+configure+my+corporate+firewall
# Only needed if TRELLO_BROKER_RESTRICT_IPS is True
BITBUCKET_IPS = getattr(
    settings,
    'TRELLO_BROKER_BITBUCKET_IPS',
    ['131.103.20.165', '131.103.20.166'],
)
