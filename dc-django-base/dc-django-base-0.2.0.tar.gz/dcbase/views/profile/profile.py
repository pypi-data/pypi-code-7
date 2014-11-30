from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView


class ProfileView(TemplateView):
    template_name = 'dcbase/profile.html'


profileView = login_required(ProfileView.as_view())
