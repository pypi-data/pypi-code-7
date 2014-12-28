import abc


class EntityLoader(metaclass=abc.ABCMeta):
    """Loads an base relation declared in the entities schema."""
    entity_type = abc.abstractproperty()
    dao_class = abc.abstractproperty()

    def __init__(self, session):
        """Initialize a new :class:`EntityLoader` instance.

        Args:
            session: a database session.
        """
        self._session = session

    def get_entities(self, data):
        """Return a list containing all entities for this loader from
        the deserialized data. If the member identified by
        :attr:`EntityLoader.entity_type` evaluates to ``False``,
        the returned list is empty.

        Args:
            data (dict): the deserialized entities.

        Returns:
            list
        """
        return data.pop(self.entity_type, None) or []

    def load(self, data):
        """Parses entities from the deserialized data and persists them
        in the data store.
        """
        for item in self.get_entities(data):
            self.full_clean(item)
            dao = self.init_dao(item)
            dao = self.persist(dao)

            # The attributes used to initialize the DAO should be
            # removed from the dictionary at this point.
            for key, value in item.items():
                self.persist_attribute(item, dao, key, value)

    def persist(self, dao):
        return self._session.merge(dao)

    def persist_attribute(self, item, dao, key, value):
        fn = "persist_{0}".format(key)
        if not hasattr(self, fn):
            return
        getattr(self, fn)(item, dao, value)

    def full_clean(self, item):
        self.validate(item)
        for key, value in item.copy().items():
            fn = "clean_{0}".format(key)
            if not hasattr(self, fn):
                continue
            getattr(self, fn)(item, value)

    def validate(self, item):
        """Validates a deserialized entity."""
        pass

    @abc.abstractmethod
    def init_dao(self, item):
        """Initializes the Data-Access Object to persist the entity."""
        raise NotImplementedError

    def __call__(self, data):
        return self.load(data)


