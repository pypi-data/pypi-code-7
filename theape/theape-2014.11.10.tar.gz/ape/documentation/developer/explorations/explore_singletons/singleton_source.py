
class SingletonTest(object):
    def __init__(self):
        self.x = 'y'
        return


def get():
    if get.test is None:
        get.test = SingletonTest()
    return get.test

get.test = None
test_instance = SingletonTest()
