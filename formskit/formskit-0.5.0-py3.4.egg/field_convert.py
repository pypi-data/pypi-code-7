class FakeConvert(object):

    def _set_field(self, field):
        self.field = field

    def __call__(self, value):
        return self.convert(value)

    def convert(self, value):
        return value

    def convert_back(self, value):
        return value

    def back(self, value):
        return self.convert_back(value)


class ToInt(FakeConvert):

    def convert(self, value):
        return int(value)

    def convert_back(self, value):
        return str(value)
