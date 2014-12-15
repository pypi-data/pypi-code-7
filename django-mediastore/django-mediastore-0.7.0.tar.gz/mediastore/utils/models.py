# -*- coding: utf-8 -*-

def order_queryset_by_pks(queryset, pks):
    object_list = dict((
        (unicode(key), value)
        for key, value in queryset.in_bulk(pks).iteritems()))
    return [object_list[unicode(pk)] for pk in pks]
