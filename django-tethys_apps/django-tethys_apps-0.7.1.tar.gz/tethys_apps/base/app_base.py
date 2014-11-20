"""
********************************************************************************
* Name: app_base.py
* Author: Nathan Swain and Scott Christensen
* Created On: August 19, 2013
* Copyright: (c) Brigham Young University 2013
* License: BSD 2-Clause
********************************************************************************
"""


class TethysAppBase(object):
    """
    Base class used to define the app class for Tethys apps.
    """
    name = ''
    index = ''
    icon = ''
    package = ''
    root_url = ''
    color = ''

    def __repr__(self):
        """
        String representation
        """
        return '<TethysApp: {0}>'.format(self.name)

    def url_map(self):
        """
        Must return a list of UrlMap objects
        """
        raise NotImplementedError()
    
    def persistent_stores(self):
        """
        Define this method to register persistent stores for your app. You may define up to 5 persistent stores for an app.

        Returns:
          list or tuple: A list or tuple of PersistentStore objects.
        """
        return None

    def dataset_services(self):
        """
        May return a list of DatasetService objects
        """
        return None