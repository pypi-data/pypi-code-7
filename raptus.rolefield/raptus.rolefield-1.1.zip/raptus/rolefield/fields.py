from Acquisition import aq_base, aq_get, aq_parent

from AccessControl import ClassSecurityInfo

from zope.interface import implements
from zope.i18n import translate

from plone.app.layout.navigation.interfaces import INavigationRoot

from Products.Archetypes.Registry import registerField
from Products.Archetypes.Registry import registerPropertyType
from Products.Archetypes.Field import Field, StringField, LinesField, STRING_TYPES, decode
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.FactoryTool import TempFolder

from raptus.rolefield import _

class RoleField(StringField):
    try:
        from Products.Archetypes.interfaces.field import IStringField
        implements(IStringField)
    except ImportError:
        __implements__ = StringField.__implements__

    _properties = StringField._properties.copy()
    _properties.update({
        'type'   : 'role',
        'role'   : '',
        'acquire': True,
        'default_acquired': False,
        'enforceVocabulary': True,
        })

    security  = ClassSecurityInfo()

    security.declarePublic('getDefault')
    def getDefault(self, instance):
        baseInstance = instance
        if self.default_acquired:
            defaultRole = type(self.default_acquired) in STRING_TYPES and self.default_acquired or self.role
            while not INavigationRoot.providedBy(instance):
                if not isinstance(instance, TempFolder):
                    for user, roles in instance.get_local_roles():
                        if defaultRole in roles:
                            return user
                instance = aq_parent(instance)
        return Field.getDefault(self, baseInstance)

    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        roles = instance.get_local_roles()
        for u, r in roles:
            if self.role in r:
                return u
        return None

    security.declarePrivate('getRaw')
    def getRaw(self, instance, **kwargs):
        return self.get(instance, **kwargs)

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        if not self.acquire and not bool(getattr(aq_base(instance), '__ac_local_roles_block__', False)):
            instance.__ac_local_roles_block__ = True
            instance.reindexObjectSecurity()
        roles = instance.get_local_roles()
        for u, r in roles:
            if self.role in r:
                r = [role for role in r if not role == self.role]
                if r:
                    instance.manage_setLocalRoles(u, r)
                else:
                    instance.manage_delLocalRoles((u,))
        instance.manage_addLocalRoles(value, (self.role,))

    security.declarePublic('get_size')
    def get_size(self, instance):
        """Get size of the stored data used for get_size in BaseObject
        """
        if self.get(instance):
            return 1
        return 0

    security.declarePrivate('validate_vocabulary')
    def validate_vocabulary(self, instance, value, errors):
        mship = getToolByName(instance, 'portal_membership')
        if not mship.getMemberById(value):
            request = aq_get(instance, 'REQUEST')
            name = self.getName()
            error = _(u'The user ${user} does not exist.',
                      mapping={'user': value})
            error = translate(error, context=request)
            errors[name] = error
            return error
        return super(RoleField, self).validate_vocabulary(instance, value, errors)

class MultiRoleField(LinesField):
    try:
        from Products.Archetypes.interfaces.field import ILinesField
        implements(ILinesField)
    except ImportError:
        __implements__ = LinesField.__implements__

    _properties = LinesField._properties.copy()
    _properties.update({
        'type' : 'multirole',
        'role' : '',
        'acquire': True,
        'default_acquired': False,
        'enforceVocabulary': True,
        })

    security  = ClassSecurityInfo()

    security.declarePublic('getDefault')
    def getDefault(self, instance):
        if self.default_acquired:
            role = type(self.default_acquired) in STRING_TYPES and self.default_acquired or self.role
            users = instance.acl_users._getAllLocalRoles(instance.getParentNode())
            default = []
            for user, roles in users.items():
                if role in roles:
                    default.append(user)
            return default
        return Field.getDefault(self, instance)

    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        roles = instance.get_local_roles()
        return [u for u, r in roles if self.role in r]

    security.declarePrivate('getRaw')
    def getRaw(self, instance, **kwargs):
        return self.get(instance, **kwargs)

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        if not self.acquire and not bool(getattr(aq_base(instance), '__ac_local_roles_block__', False)):
            instance.__ac_local_roles_block__ = True
            instance.reindexObjectSecurity()
        if type(value) in STRING_TYPES:
            value =  value.split('\n')
        value = [decode(v.strip(), instance, **kwargs)
                 for v in value if v and v.strip()]
        roles = instance.get_local_roles()
        for u, r in roles:
            if self.role in r:
                r = [role for role in r if not role == self.role]
                if r:
                    instance.manage_setLocalRoles(u, r)
                else:
                    instance.manage_delLocalRoles((u,))
        for v in value:
            instance.manage_addLocalRoles(v, (self.role,))

    security.declarePublic('get_size')
    def get_size(self, instance):
        """Get size of the stored data used for get_size in BaseObject
        """
        return len(self.get(instance))

    security.declarePrivate('validate_vocabulary')
    def validate_vocabulary(self, instance, value, errors):
        mship = getToolByName(instance, 'portal_membership')
        request = aq_get(instance, 'REQUEST')
        name = self.getName()
        error = []
        for user in value:
            if not mship.getMemberById(user):
                error.append(translate(_(u'The user ${user} does not exist.',
                                         mapping={'user': user}), context=request))
        if error:
            error = ' '.join(error)
            errors[name] = error
            return error
        return super(MultiRoleField, self).validate_vocabulary(instance, value, errors)

registerField(RoleField,
              title='Role',
              description='Used for setting a local role for a single user')

registerField(MultiRoleField,
              title='Multirole',
              description='Used for setting a local role for multiple users')

registerPropertyType('role', 'string')
