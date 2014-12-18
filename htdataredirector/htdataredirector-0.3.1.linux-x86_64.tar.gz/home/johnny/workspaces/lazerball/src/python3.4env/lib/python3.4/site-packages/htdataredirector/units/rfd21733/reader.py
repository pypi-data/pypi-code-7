from binascii import hexlify

from ...utils import millis
from .registry import Registry

class Reader:
    DEBOUNCE_DELAY = 200

    BUTTON_ZONE_MAP = {
        '10': 1,
        '20': 2,
        '40': 3,
        # These do not correspond to any zones
        #'30': None,
        #'50': None,
        #'60': None,
    }

    found_first_packet = False

    def __init__(self, io_dev):
        self.io_dev = io_dev
        self.last_hit = ''


    def __iter__(self):
        registry = Registry()
        self.unit_registry = registry.all()
        return self

    def __next__(self):
        if not self.found_first_packet:
            data = self.find_start()
            self.found_first_packet = True
        else:
            debounce_time = millis()
            data = ''
            while True: #rewrite this
                data = self.read_ascii(5)
                if (data != self.last_hit) or not self.bouncing(debounce_time):
                    break

        self.last_hit = data
        return self.parse(data)

    def find_start(self):
        while not self.found_first_packet:
            button = self.read_ascii(1)
            if button in self.BUTTON_ZONE_MAP:
                esn = self.read_ascii(4)
                if esn in self.unit_registry or not self.unit_registry:
                    self.found_first_packet = True
                    return button + esn

    def read_ascii(self, size):
        data = self.io_dev.read(size)
        return hexlify(data).decode('ascii')

    def parse(self, data):
        zone = None
        if data[0:2] in self.BUTTON_ZONE_MAP:
            zone = self.BUTTON_ZONE_MAP[data[0:2]]

        return {
            'radioId': data[2:],
            'zone': zone
        }

    def bouncing(self, debounce_time):
        return (millis() - debounce_time) < self.DEBOUNCE_DELAY
