from yowsup.layers import YowProtocolLayer
class YowTextSecureProtocolLayer(YowProtocolLayer):
    def __init__(self):
        self.handleMap = {
            "iq": (None, self.sendIq)
        }


    def sendIq(self, entity):
        self.toLower(entity.toProtocolTreeNode())