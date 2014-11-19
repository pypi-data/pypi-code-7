from __future__ import absolute_import, unicode_literals

import json

from django.core.exceptions import ValidationError
from django.forms import fields

from .conf import settings
from .widgets import SirTrevorWidget


class SirTrevorField(fields.Field):
    widget = SirTrevorWidget

    def __init__(self, blocks=None, **kwargs):
        super(SirTrevorField, self).__init__(**kwargs)
        self.blocks = blocks

    def to_python(self, value):
        try:
            value = json.loads(value)
        except ValueError:
            raise ValidationError("Invalid JSON data")
        return self.process_data(value)

    def get_blocks(self):
        blocks = self.blocks
        if blocks is None:
            blocks = settings.get_default_blocks()
        return list(b() if isinstance(b, type) else b for b in blocks)

    def process_data(self, data):
        if not isinstance(data, dict) or set(data.keys()) != set(['data']):
            raise ValidationError("Invalid JSON data")

        raw_blocks = data['data']
        if not isinstance(raw_blocks, list):
            raise ValidationError("Invalid JSON data")

        return {'data': list(self.process_blocks(raw_blocks))}

    def process_blocks(self, raw_blocks):
        block_types = self.get_blocks()
        block_type_map = dict((b.block_type, b) for b in block_types)
        for raw_block in raw_blocks:
            if raw_block['type'] not in block_type_map:
                raise ValidationError("Unknown block type")

            block_type = block_type_map[raw_block['type']]
            raw_block_data = raw_block['data']
            yield {
                'type': block_type.block_type,
                'data': block_type.clean(raw_block_data)
            }
