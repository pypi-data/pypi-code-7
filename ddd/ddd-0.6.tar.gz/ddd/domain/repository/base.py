import abc
from threading import local

from ddd.domain.repository.meta import RepositoryMeta
from ddd.domain.repository.cache import RepositoryCache


class Repository(metaclass=RepositoryMeta):
    pass
