# -*- coding: utf-8 -*-
"""
    party.py

    :copyright: (c) 2014 by Lava Lab Software Pty Ltd
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import PoolMeta
from trytond.model import fields
import abn

__metaclass__ = PoolMeta


class Party:
    __name__ = 'party.party'

    abn = fields.Char('ABN')

    @fields.depends('abn')
    def on_change_abn(self):
        self.check_abn()
        return {}

    def check_abn(self):
        """
        Validate the ABN number using the webservices
        """
        if not self.abn:
            return
        if not abn.validate(self.abn):
            self.raise_user_error("Invalid ABN number")

    @classmethod
    def validate(cls, parties):
        """
        Make validation include an abn_check
        """
        super(Party, cls).validate(parties)
        for party in parties:
            party.check_abn()
