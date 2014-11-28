import inspect




def inherit_parent_doc(func):
    print(inspect.getargspec(func))
    return func


class SuperClass:

    @classmethod
    def parent_list(cls):
        """This is parent doc"""
        return 'Ok'


class SonClass(SuperClass):

    @classmethod
    @inherit_parent_doc
    def parent_list(cls):
        """This is son doc"""
        return 'SonOk'


if __name__ == '__main__':
    print(SonClass().parent_list())
