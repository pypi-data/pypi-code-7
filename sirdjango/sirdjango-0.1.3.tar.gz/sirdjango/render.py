def render_json(data, blocks):
    if isinstance(data, dict) and isinstance(data['data'], list):
        block_map = dict((b.block_type, b) for b in blocks)
        return ''.join(render_block(raw_block, block_map) for raw_block in data['data'])


def render_block(raw_block, block_map):
    block = block_map[raw_block['type']]
    return block.render_json(raw_block['data'])
