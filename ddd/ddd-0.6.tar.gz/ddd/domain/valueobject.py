

class ValueObject(object):

    def native(self):
        """
        Returns the :class:`ValueObject` as a native Python type
        from which it can be reconstructed.
        """
        raise NotImplementedError