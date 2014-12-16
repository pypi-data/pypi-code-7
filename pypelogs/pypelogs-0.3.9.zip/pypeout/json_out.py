import json
import g11pyutils as utils

class JSONOut(object):
    def __init__(self, spec=None):
        json.JSONEncoder.default = utils.default_json_encoder  # A simple object-to-json encoder
        self.fo = utils.fout(spec)

    def process(self, pin):
        for e in pin:
            self.fo.write(json.dumps(e))
            self.fo.write("\n")
            self.fo.flush()