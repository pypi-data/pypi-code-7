# -*- coding: utf-8 -*-

"""Get settings from a specified settings.py module, using a separate
   process to prevent pollution of our namespace.
"""
from dk.dkimport import dkimport

import os
import multiprocessing


def _getsettings(q, settingsmodule):
    cur = os.environ.get('DJANGO_SETTINGS_MODULE')
    os.environ['DJANGO_SETTING_MODULE'] = settingsmodule
    from django.conf import settings
    import cms  # django-cms seriously mangles the settings

    def _module_contents(m):
        return dict((k, getattr(m, k))
                    for k in dir(m) if k.upper() == k)

    res = _module_contents(settings)
    res.update(_module_contents(dkimport(settingsmodule)))
    q.put(res)


def getsettings(settingsmodule):
    """Return a dict containing the settings from `settingsmodule`
       (format: 'xxxxx.site.settings').
    """
    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=_getsettings, args=(q, settingsmodule))
    p.run()
    res = q.get()
    q.close()
    return res
