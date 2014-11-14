# -*- coding: utf-8 -*-

import csv

from django.http import HttpResponse

_CP_NAME = u'attachment; filename="{}"'


def objgetattr(obj, key):
    keys = key.split('.')
    ans = obj
    for key in keys:
        ans = getattr(ans, key)
    return ans


class CsvMixin(object):
    csv_fields = None
    csv_name = None

    def render_to_response(self, context, **response_kwargs):
        if 'csv' in context and context['csv']:
            response = HttpResponse(content_type='text/csv')

            if not self.csv_name:
                self.csv_name = 'file.csv'

            response['Content-Disposition'] = _CP_NAME.format(self.csv_name)

            writer = csv.writer(response)
            writer.writerow(self.csv_fields)
            for delivery in self.object_list:
                writer.writerow(
                    [
                        unicode(  # noqa
                            objgetattr(delivery, key)
                        ).encode('utf8')
                        for key in self.csv_fields
                    ]
                )
            return response
        else:
            return super(
                CsvMixin,
                self
            ).render_to_response(
                context,
                **response_kwargs
            )
