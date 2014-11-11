from django.conf import settings

BITBUCKET_SETTINGS = getattr(settings, 'DEPLOY_BITBUCKET_SETTINGS', {
    'username' 		: '',
    'password' 		: '',
})

GITHUB_SETTINGS = getattr(settings, 'DEPLOY_GITHUB_SETTINGS', {
    'username' 		: '',
    'password' 		: '',
})
