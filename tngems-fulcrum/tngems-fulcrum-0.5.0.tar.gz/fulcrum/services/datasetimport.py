


class DatasetImportService(object):

    def __init__(self, session):
        """Initialize a new :class:`DatasetImportService` instance.

        Args:
            session: a database session object.

        """
        self._session = session

    def load_many(self, files):
        """Load fixtures given a list of filepaths."""
        pass
