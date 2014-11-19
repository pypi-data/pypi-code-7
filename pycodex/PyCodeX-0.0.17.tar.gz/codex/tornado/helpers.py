def echo(self, value):
    if value is None or value is False:
        return ''
    elif value is True:
        return '1'
    return value