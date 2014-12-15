# -*- coding: utf-8 -*-

import os

from .stores import Stores
from .formats import Formats
from .stack_trace import StackTrace


class Reporter(object):

    def __init__(self, credentials, store_name):
        store_cls = getattr(Stores, store_name)
        self.store = store_cls(credentials=credentials)

    def report(self, **kwargs):
        trace_info = StackTrace()
        title_format = kwargs.pop('title_format', Formats.title)
        body_format = kwargs.pop('body_format', Formats.body)

        culprit = Formats.culprit.format(
            filepath=trace_info.filepath, lineno=trace_info.lineno,
            exception=trace_info.exception.__name__)

        title = title_format.format(
            exception=trace_info.exception.__name__,
            filename=os.path.basename(trace_info.filepath),
            method_name=trace_info.method_name)

        body = "{}".format(
            body_format.format(stack_trace=trace_info.stack_trace_text))

        if kwargs.pop('include_locals', False):
            body = "{} {}".format(
                body, Formats.locals_format.format(
                    locals_data=trace_info.locals_data)
            )

        extra_content = kwargs.pop('extra_content', '')

        if extra_content:
            body = "{}\n\nExtra Content:\n{}".format(
                body, extra_content
            )

        if kwargs.get('request'):
            body = "{} {}".format(
                body, Formats.request_data.format(
                    request_data=str(kwargs.get('request'))
                )
            )

        body = """{}

{}
""".format(body, culprit)

        return self.store.create_or_update_issue(
            title=title, body=body, culprit=culprit, **kwargs)
