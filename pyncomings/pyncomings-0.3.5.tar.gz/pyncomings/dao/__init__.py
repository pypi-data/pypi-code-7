# Authors: Pablo Saavedra
# Contact: saavedra.pablo@gmail.com

"""
This package contains Pycomings DAO modules.
"""


class DAOEntry(object):

    """
    Abstract base class for pycomings DAOEntry.

    Each writer module or package must export a subclass also called
    'DAOEntry'.

    The `send()` method is the main entry point.
    """


    def create_table():
        """
        Normally not overridden or extended in subclasses.
        """
        raise NotImplementedError

    def create_entry(self, entry):
        """
        Normally not overridden or extended in subclasses.
        """
        raise NotImplementedError

    def get_entry(self, entry_id):
        """
        Normally not overridden or extended in subclasses.
        """
        raise NotImplementedError

    def get_entries(self, offset=None, max_items=None):
        """
        Normally not overridden or extended in subclasses.
        """
        raise NotImplementedError

    def update_entry(self, entry):
        """
        Normally not overridden or extended in subclasses.
        """
        raise NotImplementedError

    def delete_entry(self, entry_id):
        """
        Normally not overridden or extended in subclasses.
        """
        raise NotImplementedError

    def search_entry_by_path(self, path):
        """
        Normally not overridden or extended in subclasses.
        """
        raise NotImplementedError

    def search_entry_by_date(self, date):
        """
        Normally not overridden or extended in subclasses.
        """
        raise NotImplementedError


