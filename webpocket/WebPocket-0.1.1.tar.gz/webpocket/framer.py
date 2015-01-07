# -*- coding: utf-8 -*-

from struct import pack
from frame import *
from exc import *

class Framer(object):
  def __init__(self, actors):
    self._actors = actors
    self._buffer = b''

  def send_text(self, text):
    data = Frame(opcode=OPCODE_TEXT, payload=text).encode()
    self._actors['streamer'].send(data)

  def send_binary(self, binary):
    data = Frame(opcode=OPCODE_BINARY, payload=binary).encode()
    self._actors['streamer'].send(data)

  def feed(self, data):
    self._buffer += data
    while len(self._buffer) > 0:
      try:
        frame, left_data = Frame().decode(self._buffer)
        self._buffer = left_data
        self._actors['messager'].feed(frame)
      except InsufficientBytesException:
        break

  def send_pong(self):
    data = Frame(opcode=OPCODE_PONG).encode()
    self._actors['streamer'].send(data)

  def send_close(self, code, reason):
    payload = pack('!H', code) + reason
    data = Frame(opcode=OPCODE_CLOSE, payload=payload).encode()
    self._actors['streamer'].send(data)

if __name__ == '__main__':
  class DummyMessager(object):
    def feed(self, frame):
      frame.inspect()

  messager = DummyMessager()
  framer = Framer({'messager': messager})

  data = Frame(payload='foobar').encode()
  framer.feed(data[:3])
  framer.feed(data[3:])
