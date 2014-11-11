from socle.facts import ARCH

class GenericBoard(object):
    NAME = "Generic " + ARCH

    @classmethod
    def instantiate(cls, *args):
        return cls(*args)


    def mainmenu(self):
        return ()
