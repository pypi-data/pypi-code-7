from collections import namedtuple
from dcbase.lib.navLink import NavLink
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

ProfileModel = namedtuple('ProfileModel', ['model', 'editUrl', 'name'])

class ProfileEditor(object):
    _profileModels = []

    @classmethod
    def add_profile_edit_context(cls, context, navName, panelName):
        navLinks = [
            NavLink(_('User'), reverse('account_profile_edit')),
            NavLink(_('Change Password'), reverse('account_change_password')),
            NavLink(_('E-mail'), reverse('account_email')),
            NavLink(_('Social Accounts'), reverse('socialaccount_connections')),
        ]
        for profileModel in cls.get_profile_models():
            navLinks.append(NavLink(profileModel.name, profileModel.editUrl))

        context['profileNavLinks'] = navLinks
        context['selectedProfileNavLink'] = navName
        context['profilePanelHeading'] = panelName

    @classmethod
    def register_profile_model(cls, model, profile_url, nav_name):
        cls._profileModels.append(ProfileModel(model, profile_url, nav_name))

    @classmethod
    def get_profile_models(cls):
        return cls._profileModels


