# -*- coding: utf-8 -*-

"""Retrieve meta information about models, in an easy to debug format.
   This module hacks at Django internals to make them easier to work with.
"""

# pylint: disable=E1101,R0903,R0902,W0212,C0301,W0201

# E1101: module html has no tr member
# R0903: too few public methods.
# R0902: too many instance attributes.
# W0212: access to privates
# C0301: line too long because Django_occationally_uses_very_long_names...
# W0201: attribute defined outside __init__

import sys
import inspect
import pprint

import types
from django.db import models

from dk.collections import pset
from dk import html as _html


def info(x):
    """Retrieve meta info for the model.
       x can be either a Model class or an instance. The field lists are
       stored in dictionary like objects that can be iterated over directly
       and will produce the fields in definition order.

          for name, value in info(myModel).fields:
             ...
    """
    if inspect.isclass(x) and issubclass(x, orm.Record):
        return x.info()
    if isinstance(x, orm.Record):
        return x.__class__.info()
    
    # this might seem unintuitive, but it's correct (metaclasses behind
    # the curtain...)
    if isinstance(x, models.Model):
        return ModelInfo(x.__class__, x)
    else:
        return ModelInfo(x)


def html(obj):
    "Output a debug version of obj as html."
    i = info(obj)
    rows = [_html.tr(_html.th(i.name, colspan=2))]
    for f in i.fieldnames:
        val = getattr(obj, f)
        if type(val) == str:
            val = val.decode('u8').encode('l1')
        else:
            val = str(val)
        rows.append(
            _html.tr(
                _html.th(f),
                _html.td(_html.escape(val))))
    return str(_html.table(rows, align='center', border=1))
    

########################################################################
#  Interface to this module is above, implementation details below.
#  (you shouldn't need to call any of these yourself).

class FieldInfo(object):
    "Meta info about a field."
    def __init__(self, field):
        self.field = field
        self.attrs = [a for a in dir(field) if not a.startswith('__')]

    def __repr__(self):
        res = ['Field(%s):' % self.field.attname]
        for attr in self.attrs:
            val = getattr(self.field, attr)
            if type(val) != types.MethodType:
                val = repr(val)
                res.append('  %s = %s' % (attr, val))
        return '\n'.join(res)

    
class FieldAttrs(pset):
    """Convenience class for introspecting field attributes, its repr()
       prints like::
       
         telefon.attname = 'telefon'
         telefon.blank = True
         telefon.column = 'telefon'
         etc.

    """
    def __init__(self, kind, field):
        from django.db import connection   # needed to look up backend params
        self._field = field
        super(FieldAttrs, self).__init__()
        attrs = [a for a in dir(field) if not a.startswith('__')]
        for attr in attrs:
            fval = getattr(field, attr)
            if str(type(fval)) == "<class 'django.utils.functional.__proxy__'>":
                fval = unicode(fval)
            if not isinstance(fval, types.MethodType):
                self[attr] = fval
        self['formfield'] = field.formfield()
        self['internal_type'] = field.get_internal_type()
        self['db_type'] = field.db_type(connection=connection)
        
        if kind == 'm2m':
            # Django is in the process of overwriting the help_text, when it
            # does (django/db/models/fields/related.py[760]):
            #
            #    self.help_text = string_concat(self.help_text, ' ', msg)
            #
            # Where msg is the localized version of "Hold down Ctrl or Cmd
            # to ...."
            # string_concat() is a lazy'ied function
            # (django.util.functional.lazy).
            # The lazy() function returns an instance of class __proxy__
            # where the three arguments (help_text, single space, and msg)
            # are assigned (as a tuple) to self.__args.
            #
            # Python says self.__args => _proxy____args (as used below).

            self['help_text'] = field.help_text._proxy____args[0]
        try:
            default = self['default']
            if str(default).endswith('NOT_PROVIDED'):
                self['default'] = ''
        except:
            pass

    def get_choices(self, include_blank=True, blank_choice=None):
        "Return the list of choices for model fields where these are defined."
        if blank_choice is None:
            blank_choice = [('', '--------')]
        return self._field.get_choices(include_blank, blank_choice)

    def __repr__(self):
        res = []
        attname = self._field.attname
        for k, v in self:
            if v or not v:
                res.append('%s.%s = %s' % (attname, k, repr(v)))
        return '\n'.join(res)

    def __str__(self):
        return '<Field: %s>' % self._field.attname


#  helper functions for ModelInfo (below)


def _foreignkeys(fields):
    res = pset()
    for field in fields:
        if field.attname.endswith('_id'):
            res[field.attname[:-3]] = field
    return res


def _fieldname(field):
    if field.attname.endswith('_id'):
        return field.attname[:-3]
    else:
        return field.attname


def _raw_fields(fields):
    res = pset()
    for field in fields:
        res[_fieldname(field)] = field

    return res


def adminOptions(model):
    """Seems like _meta.admin is deprecated...
       There's probably much better ways, but I heart hackery :-)
    """
    try:
        appname = model.__module__.rsplit('.', 1)[0]
        admin_module = appname + '.admin'
        __import__(admin_module)
    except:
        #raise
        return None
    else:
        return getattr(sys.modules[admin_module], model.__name__ + 'Options', None)


class DjangoField(object):
    "Introspection for a Django Field."

    def __init__(self, field):
        from django.db import connection
        self.field = field
        f = field
        self.name = f.attname
        self.dbtype = f.db_type(connection=connection)
        self.formfield = f.formfield().__class__.__name__
        #f.m2m_column_name()   post_id
        #f.m2m_reverse_name()  posttype_id
        #

    def __repr__(self):
        return '%s(%s, %s)' % (self.name, self.formfield, self.dbtype)
    

class DjangoModel(object):
    "Introspection for a Django Model."

    def __init__(self, model):  # pylint:disable=R0915
        self.meta = model._meta
        m = self.meta

        try:
            self._field_cache = m._field_cache
            self._join_cache = m._join_cache
        except AttributeError:
            self._field_cache = None
            self._join_cache = None
        try:
            self.m2m_cache = m._m2m_cache
        except AttributeError:
            self.m2m_cache = None
        self.abstract = m.abstract 
        self.admin = m.admin 
        self.app_label = m.app_label 
        self.auto_field = m.auto_field 
        self.db_table = m.db_table 
        self.db_tablespace = m.db_tablespace 
        self.duplicate_targets = m.duplicate_targets 
        self.get_latest_by = m.get_latest_by 
        self.has_auto_field = m.has_auto_field 
        self.installed = m.installed 
        self.module_name = m.module_name 
        self.object_name = m.object_name
        # Fix Django version 1.1.4
        #self.one_to_one_field = m.one_to_one_field
        self.order_with_respect_to = m.order_with_respect_to 
        self.ordering = m.ordering 
        self.parents = m.parents 
        self.permissions = m.permissions 
        self.pk = m.pk 
        self.unique_together = m.unique_together 
        self.verbose_name = m.verbose_name 
        self.verbose_name_plural = m.verbose_name_plural 
        #self.verbose_name_raw = m.verbose_name_raw 

        self._fields = m._fields()
        self._fill_m2m_cache = m._fill_m2m_cache()
        self._fill_related_many_to_many_cache = m._fill_related_many_to_many_cache()
        self._fill_related_objects_cache = m._fill_related_objects_cache()
        self._many_to_many = m._many_to_many()
        self.add_permission = m.get_add_permission()
        self.all_field_names = m.get_all_field_names()
        self.all_related_m2m_objects_with_model = m.get_all_related_m2m_objects_with_model()
        self.all_related_many_to_many_objects = m.get_all_related_many_to_many_objects()
        self.all_related_objects = m.get_all_related_objects()
        self.all_related_objects_with_model = m.get_all_related_objects_with_model()
        self.change_permission = m.get_change_permission()
        # Upgrade r8630:
        #self.data_holders = m.get_data_holders()
        self.delete_permission = m.get_delete_permission()
        self.fields_with_model = m.get_fields_with_model()
        # Upgrade r8630:
        #self.follow = m.get_follow()
        #self.followed_related_objects = m.get_followed_related_objects()
        self.m2m_with_model = m.get_m2m_with_model()
        self.ordered_objects = m.get_ordered_objects()
        self.parent_list = m.get_parent_list()
        self.init_name_map = m.init_name_map()
        
        self.local_fields = [DjangoField(f) for f in m.local_fields]
        self.local_many_to_many = [DjangoField(f) for f in m.local_many_to_many]
        self.many_to_many = [DjangoField(f) for f in m.many_to_many]

    def _all_fields(self):
        "Return all fields with type code."
        res = pset()
        
        for f in self._fields:
            if f.name.endswith('_id'):
                res[f.name[:-3]] = 'fk', f
            else:
                res[f.name] = 'local', f
        for f in self.local_many_to_many:
           res[f.name] = 'm2m', f.field
#        for f in self.all_related_objects:
#            if f.name.endswith('_id'):
#                res[f.name[:-3]] = 'fk', f
        
        return res

    def all_fields(self):
        "Return all fields."
        res = pset()

        for fname, (_tp, f) in self._all_fields():
            res[fname] = f

        return res

    def fkeys(self):
        "Return only foreign keys."
        res = pset()

        for fname, (tp, f) in self._all_fields():
            if tp == 'fk':
                res[fname] = f

        return res

    def m2m(self):
        "Return only m2m fields."
        res = pset()

        for fname, (tp, f) in self._all_fields():
            if tp == 'm2m':
                res[fname] = f

        return res

    #def field(self, name):
    #    return self.meta.get_field_by_name(name)

    def __repr__(self):
        klen = max(len(k) for k in self.__dict__.keys())
        for k in sorted(self.__dict__.keys()):
            val = self.__dict__[k]
            if isinstance(val, list):
                sval = pprint.pformat(val, width=40)
                print k.rjust(klen)
                for line in sval.splitlines():
                    print ' ' * klen, line
            else:
                print k.rjust(klen), str(self.__dict__[k])[:80]
        return ''
        #return pprint.pformat(self.__dict__, width=100)


class ModelInfo(object):
    "Facade pattern class to access model._meta."
    
    def __init__(self, model, obj=None):
        self.is_model = True
        self.is_orm = False

        if isinstance(model, basestring):
            print "MODEL IS STRING:", model
        opts = model._meta   # pylint: disable=W0212
        self.opts = opts
        self.model = model
        self.obj = obj
        self.name = opts.object_name
        self.db_table = opts.db_table
        self.module_name = opts.module_name

        self.admin = adminOptions(model)

        if self.admin is not None:
            self.list_display = self.admin.list_display
            self.search_fields = self.admin.search_fields
            self.field_layout = self.admin.fields
            self.list_per_page = self.admin.list_per_page
        else:
            self.list_display = ()
            self.search_fields = ()
            self.field_layout = ''
            self.list_per_page = 100

        self.dm = DjangoModel(model)
        
        self.fields = self.dm.all_fields()
        self.foreign = self.dm.fkeys()
        self.m2m = self.dm.m2m()
        
        #self.field_info = self._fields(opts.fields)
        
        self.fieldnames = [f for (f, _) in self.fields]

    @property
    def field_info(self):
        """Returns a read-only list of fields for the model.
           The fields are actually a shadow of the instance vars.
        """
        if not hasattr(self, '_field_info'):
            tmp = []
            for fname, (tp, field) in self.dm._all_fields():
                finfo = FieldAttrs(tp, field)
                tmp.append((
                    field.creation_counter,
                    fname,
                    finfo))
            tmp.sort()

            res = pset()
            for _, k, v in tmp:
                res[k] = v
            
            self._field_info = res

        return self._field_info

    def printopts(self):
        "Pretty-print opts."
        atts = [att for att in dir(self.opts) if not att.startswith('__')]
        for att in atts:
            print att.rjust(40), getattr(self.opts, att, 'None')

    def __str__(self):
        res = ['class %s:' % self.name]
        attrs = [
            shorten_line('name', self.name),
            shorten_line('db_table', self.db_table),
            shorten_line('module_name', self.module_name),
            shorten_line('list_display', self.list_display),
            shorten_line('search_fields', self.search_fields),
            shorten_line('list_per_page', self.list_per_page),
            shorten_line('fields', self.fieldnames),
            pretty_line('field_layout', self.field_layout),
            ]

        return '\n'.join(res + attrs)

    __repr__ = __str__
    
########################################################################


class PrettySet(pset):
    "pset that prints itself prettily on a console."
    def __init__(self, name):
        self._name = name
        super(PrettySet, self).__init__()

    def __repr__(self):
        res = ['class %s:' % self._name]
        for k, v in self:
            if k == 'field_layout':
                res.append(pretty_line(k, v))
            else:
                res.append(shorten_line(k, v))
        return '\n'.join(res)


def indent(txt, n):
    "Indent lines in txt 'n' spaces. Returns a string (not lines)."
    lines = txt.split('\n')
    return '\n'.join((' ' * n) + line for line in lines)


def pretty_line(k, v):
    "Specialized pretty-print line."
    k = str(k)
    vstr = repr(v)
    fixed = 7
    
    if len(k) + len(vstr) + fixed > 72:
        vstr = pprint.pformat(v, 1, 72)
        leading = vstr[0]
        vstr = indent(' ' + vstr[1:], 8)
        return '    %s = %s\n%s' % (k, leading, vstr)
    else:
        return '    %s = %s' % (k, vstr)


def close_openers(s):
    """Pretty print lists, so that the ... appears to be inside a balanced
       set of parens.
    """
    stack = []
    squote = False
    dquote = False
    for c in s:
        if c in "([<":
            stack.append(c)
        elif c in ")]>":
            stack.pop()
        elif c == "'":
            squote = not squote
        elif c == '"':
            dquote = not dquote
        else:
            pass
    close = ''
    if squote:
        close += "'"
    if dquote:
        close += '"'
    for c in reversed(stack):
        if c == '(':
            close += ')'
        elif c == '[':
            close += ']'
        elif c == '<':
            close += '>'

    return s + '...' + close


def shorten_line(k, v, length=72):
    "Crop line length, but cut inside parens."
    s = '    %s = %s' % (k, repr(v))
    if len(s) > length:
        return close_openers(s[:length])
    else:
        return s
