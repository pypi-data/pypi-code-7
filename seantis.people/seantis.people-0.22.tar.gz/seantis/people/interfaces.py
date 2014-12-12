
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.directives import form

from z3c.relationfield.schema import RelationChoice

from zope import schema
from zope.interface import Interface, Attribute

from seantis.people import _


class ISeantisPeopleSpecific(Interface):
    pass


class IPersonMarker(Interface):
    pass


class IPerson(Interface):

    def memberships(self):
        """ A dictionary of membership belonging to this person, keyed by
        organization (brain or object with a title and an url)."""


class INameFromPerson(Interface):
    pass


class IList(form.Schema):
    """ A list of IPerson objects. """

    title = schema.TextLine(
        title=_(u"Name of the list of people"),
        required=True
    )

    people_per_page = schema.Int(
        title=_(u"Number of people shown on each page"),
        required=True,
        default=50
    )


class IMembershipSource(Interface):

    def memberships(self, person=None):
        """ Return a dictionary of objects providing IMembership. The key
        of the dictionary is the uuid of the organization (object with url and
        title).

        If a person object (not a brain) is given, only the memberships
        of that person are returned.
        """


class IMembershipChangedEvent(Interface):
    """ This event needs to be signaled when the membership in a
    IMembershipSource object changed. That means if a membership was added,
    removed or an attribute it was changed (start, end, role).

    """

    person = Attribute("The person whose membership has changed.")


class IMembership(form.Schema):

    role = schema.TextLine(
        title=_(u"Role inside organization"),
        required=True
    )

    person = RelationChoice(
        title=_(u"Person"),
        source=ObjPathSourceBinder(
            object_provides=IPersonMarker.__identifier__
        ),
        required=True,
    )

    note = schema.TextLine(
        title=_(u"Note"),
        description=_(u"General note about this membership"),
        required=False
    )


class ICompoundColumns(Interface):

    def get_compound_columns(self):
        """ Return a dictionary of compound columns. See
        seantis.people.supermodel.schema_columns for more.

        """
