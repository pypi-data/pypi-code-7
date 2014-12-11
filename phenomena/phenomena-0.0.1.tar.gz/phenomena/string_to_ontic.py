from ontic.ontic_type import perfect_object, OnticType

type_transformer = {
    int: lambda v: int(v)
}

def transform(ontic_type, data):
    if not issubclass(ontic_type, OnticType):
        raise ValueError('"ontic_type" parameter is not subclass OnticType.')
    if not isinstance(data, dict):
        raise ValueError('"data" parameter is not of type dict.')

    ontic_object = ontic_type()
    ontic_schema = ontic_type.get_schema()
    for name in ontic_schema.keys():
        str_value = data.get(name)

        if not str_value:
            ontic_object[name] = None
            continue

        value_type = ontic_schema[name].type
        if value_type:
            ontic_object[name] = type_transformer[value_type](str_value)
        else:
            ontic_object[name] = str_value

    perfect_object(ontic_object)
    return ontic_object
