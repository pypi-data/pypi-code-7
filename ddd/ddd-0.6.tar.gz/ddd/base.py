from ddd.event.publisher import get_publisher


class DDDObject(object):

    @property
    def publisher(self):
        get_publisher()


