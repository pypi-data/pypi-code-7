def set_default(tag):
    if not tag:
        tag = 'default'

    return tag


def parse(tag):
    if hasattr(tag, '__iter__'):
        tag = ','.join(tag)

    return tag


def unpack(tags):
    if ',' in tags:
        tag_list = tags.split(',')
    else:
        tag_list = []
        tag_list.append(tags)

    return tag_list
