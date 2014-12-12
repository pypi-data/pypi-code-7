from plone.dexterity.content import Container
from seantis.people.interfaces import IPerson
from seantis.people import _


class PersonBase(Container):

    @property
    def memberships(self):
        return IPerson(self).memberships()

    @property
    def organizations(self):
        return IPerson(self).organizations()

    @property
    def organization_uuids(self):
        return IPerson(self).organization_uuids()

    @property
    def membership_fields(self):
        return {
            'memberships': _(u'Memberships')
        }
