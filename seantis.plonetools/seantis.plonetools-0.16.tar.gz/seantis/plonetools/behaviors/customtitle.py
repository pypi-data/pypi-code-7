from plone.app.content.interfaces import INameFromTitle
from zope.interface import implements, Interface
from zope.component import adapts


class ICustomTitle(Interface):
    pass


class CustomTitle(object):
    """ Calls get_custom_title on a dexterity type's class to get the
    title and id on creation. To use add the following to your dexterity
    type xml:

    <!-- enabled behaviors -->
    <property name="behaviors">
        <element
            value="seantis.plonetools.behaviors.customtitle.ICustomTitle"
        />
    </property>

    And add get_custom_title to your class defined in <property name="klass">:

    def get_custom_title(self):
        return u'My custom title'

    """
    implements(INameFromTitle)
    adapts(ICustomTitle)

    def __init__(self, context):
        pass

    def __new__(cls, context):
        title = context.get_custom_title()
        instance = super(CustomTitle, cls).__new__(cls)

        instance.title = title
        context.setTitle(title)

        return instance


def on_object_modified(obj, event=None):
    obj.setTitle(obj.get_custom_title())
    obj.reindexObject()
