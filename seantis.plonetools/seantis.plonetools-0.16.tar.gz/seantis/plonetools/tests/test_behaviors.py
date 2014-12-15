from plone import api
from plone.dexterity.content import Container

from seantis.plonetools import tests
from seantis.plonetools.behaviors.customtitle import on_object_modified


class CustomTitleContainer(Container):

    def get_custom_title(self):
        return self.custom_title


class TestBehaviors(tests.IntegrationTestCase):

    def test_custom_title_behavior(self):

        behavior = 'seantis.plonetools.behaviors.customtitle.ICustomTitle'
        klass = 'seantis.plonetools.tests.test_behaviors.CustomTitleContainer'

        portal_type = self.new_temporary_type(
            behaviors=[behavior], klass=klass
        ).id

        with self.user('admin'):
            obj = api.content.create(
                id='',
                type=portal_type,
                container=self.new_temporary_folder(),
                custom_title=u'My custom title'
            )

        self.assertEqual(obj.id, 'my-custom-title')
        self.assertEqual(obj.title, u'My custom title')

        obj.custom_title = u'Another swell title'
        on_object_modified(obj)

        # the id does not change after initial creation
        self.assertEqual(obj.id, 'my-custom-title')
        self.assertEqual(obj.title, u'Another swell title')
