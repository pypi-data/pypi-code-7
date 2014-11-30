from dcbase.tests.unit import UnitTestCase
from dcbase.tests.unit.view.mixin import RequiresLogin
from django.core.urlresolvers import reverse


class TestProfileView(UnitTestCase, RequiresLogin):
    url = reverse('account_profile')

    def test_rendersProfileTemplate(self):
        self.user = self.createUser(logIn=True)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'dcbase/profile.html')
