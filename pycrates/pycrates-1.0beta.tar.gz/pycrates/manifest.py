from abc import ABCMeta, abstractmethod

import dateutil.parser


class IField(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def dumps(self, value):
        return value

    @abstractmethod
    def loads(self, value):
        return value


class Field(IField):
    def dumps(self, value):
        return value

    def loads(self, value):
        return value


class DateTimeField(IField):
    def dumps(self, value):
        return value.isoformat()

    def loads(self, value):
        return dateutil.parser.parse(value)
