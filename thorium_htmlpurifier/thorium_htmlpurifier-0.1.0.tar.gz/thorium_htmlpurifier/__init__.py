# -*- coding: utf-8 -*-

from purifier.purifier import HTMLPurifier
from purifier.whitelist import WHITELIST

from thorium.fields import CharField
from thorium.validators import CharValidator


class HTMLValidator(CharValidator):

    purifier = HTMLPurifier(WHITELIST, validate=True)

    def additional_validation(self, value):
        super().additional_validation(value)
        self.purifier.feed(value)


class HTMLField(CharField):
    validator_type = HTMLValidator
