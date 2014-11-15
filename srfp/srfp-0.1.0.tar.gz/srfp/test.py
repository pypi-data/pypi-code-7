from . import protocol, comms

import begin

@begin.start
def test(address):
	"""Send a test message."""

	sock = comms.open(address)
	msg = protocol.NodeInfoRequest((b'C', b'DOS', b'RUN')).encode(1)
	sock.send(msg)
