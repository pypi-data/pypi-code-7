import yaml


class Serializer(object):
    """Responsible for serializing and deserializing Fulcrum datasets."""
    content_type = "text/yaml"
    default_indent = 4

    def serialize(self, data, *args, **kwargs):
        kwargs.setdefault('default_flow_style', False)
        kwargs.setdefault('indent', self.default_indent)
        return yaml.safe_dump(data, *args, **kwargs)

    def deserialize(self, raw_data):
        return yaml.safe_load(raw_data)
