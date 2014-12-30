

class EntityInspector(object):
    """
    Provides an interface to inspect domain entities. For internal
    usage only.
    """

    def get_property(self, entity, name):
        return entity.__properties__[name].get(entity)

    def as_tuple(self, entity):
        """Project the domain object as a named tuple."""
        #args = []
        #for p in entity.__properties__.keys():
        #    value = p.get(entity)
        return entity._tuple_cls(*[
            self.get_property(entity, x) for x in entity.__properties__.keys()])
