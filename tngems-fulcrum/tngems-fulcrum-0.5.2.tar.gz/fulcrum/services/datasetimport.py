import logging

from libsovereign.const import ROOT_USER_ID

from fulcrum.const import LOGGER_NAME_CONSOLE
from fulcrum.transaction import AuthorizedTransaction


class DatasetImportService(object):

    def __init__(self, serializer, session, loaders=None, logger=None):
        """Initialize a new :class:`DatasetImportService` instance.

        Args:
            serializers: an object exposing the serializer interface.
            session: a database session object.
            loaders (fulcrum.loader.EntityLoader): concrete implementations
                of :class:`~fulcrum.loader.EntityLoader.
        """
        self._serializer = serializer
        self._session = session
        self._loaders = loaders or []
        self._logger = logger or logging.getLogger(LOGGER_NAME_CONSOLE)

    def load_many(self, files):
        """Load fixtures given a list of filepaths."""
        for filename in files:
            self.load(filename)

    def load(self, filename):
        """Loads the entities specified in `filename`."""
        with open(filename, 'r') as f:
            data = self._serializer.deserialize(f.read())
        with AuthorizedTransaction(self._session, ROOT_USER_ID, 0):
            for loader in self._loaders:
                loader(data)
