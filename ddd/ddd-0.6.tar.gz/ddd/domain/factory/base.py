import abc


class Factory(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def create(self, *args, **kwargs):
        """Create a new instance of the domain model specified for
        the factory."""
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        return self.create(*args, **kwargs)