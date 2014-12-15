# -*- coding: utf-8 -*-

"""
exporter.exporter
~~~~~~~~~~~~~~~~~

This module implements interface for Exporter library.
:copyright: (c) 2014 by Vedarth Kulkarni.
:license: MIT, see LICENSE for more details.

"""

from .reporter import Reporter


def report_issue(credentials, store_name, **kwargs):
    '''Reports an issue for any exception in application code to the specified store.

    :params credentials: object of store specific credentials from `exreporter.credentials`
    :params store_name: name of the issue store eg: 'github'
    :params title_format: (optional) string to specify the format of issue title
    :params body_format: (optional) string to specify the format of issue body
    :params extra_content: (optional) extra content that is to be added to issue body
    :params max_comments: (optional) maximum number of comments after which new issue is to be created, default value is ``50``
    :params time_delta: (optional) specifies minimum time interval after which issue should be reported if the exceptions occurs multiple times
    :params include_locals: (optional) boolean specifying whether dump of ``locals`` should be included in issue body
    :params labels: (optional) list of labels that are to be applied to the issue, default: ``['Bug']``
    '''
    kwargs.setdefault('max_comments', 50)
    kwargs.setdefault('time_delta', 10)
    kwargs.setdefault('include_locals', True)
    kwargs.setdefault('labels', ['Bug'])
    reporter = Reporter(credentials=credentials, store_name=store_name)
    return reporter.report(**kwargs)


def report_github_issue(credentials, **kwargs):
    '''Reports the exception to Github by calling ``report_issue``.

    :param credentials: object of :class:`GithubCrdentials` with correct github credentials
    :param \*\*kwargs: Optional arguments that ``report_issue`` takes.

    Returns :class:`GithubIssue` object.
    '''
    return report_issue(
        credentials=credentials, store_name='github', **kwargs)
