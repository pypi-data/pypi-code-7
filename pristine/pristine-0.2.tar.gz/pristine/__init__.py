"""
Entity module for the GuestList Project
"""

from cerberus import Validator

class Entity(object):

    schema = {}

    def __init__(self, data):
        self._data = data
        self.validator = Validator(self.schema) 
        self.validation_errors = {}


    def validate(self):
        """
        Validate methods for the entity based on its
        internal schema (see tests for example)
        """
        valid = self.validator.validate(self._get_relevant_data())
        self.validation_errors = self.validator.errors
        return valid

    def _get_relevant_data(self):
        data = {}
        for k in self.schema.keys():
            try:
                data[k] = self._data[k] 
            except KeyError:
                pass

        return data

    def to_dict(self):
        return self._get_relevant_data()
