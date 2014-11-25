"""
Entity module for the GuestList Project
"""

from cerberus import Validator

class Entity(object):

    schema = {}

    def __init__(self, data):
        self._data = data
        self.validator = Validator(self.schema) 


    def validate(self):
        """
        Validate methods for the entity based on its
        internal schema (see tests for example)
        """
        
        return self.validator.validate(self._get_relevant_data())

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
