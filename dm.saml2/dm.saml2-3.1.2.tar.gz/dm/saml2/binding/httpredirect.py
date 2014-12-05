# Copyright (C) 2010-2014 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
"""Support for the http redirect binding.

The redirect binding allows to transport an SAML2 message
(request or response) via query string parameters in an HTTP ``GET``
request, usually used via an HTTP redirect.

Due to space considerations, the transported message usually
cannot contain a signature. The redirect binding supports
a restricted form of signature for the message's top level.
The implementation here provides the parameters for this signature
support but does not (yet) really implements signing and verification.
Such an implementation requires extension of ``PyXMLsec`` (the
Python binding to the xml security library) or a separate implementation
of the signing and verification algorithms.
"""

from zlib import compress, decompress
from urllib import urlencode
from cgi import parse_qs

from ..pyxb.protocol import ResponseType
import dm.saml2.config as config


def encode(url, message, relay_state=None, context=None):
  """encode *message* and *relay_state* as query parameters for *url*; return the extended url.

  *message* is a ``PyXB`` binding object representing either a request or
  response.

  *relay_state* is a string, usually an opaque state handle obtained from
  a relay state manager. In cases, where an unsolicited response is
  sent, *relay_state* can indicate in some way a target.

  *context* is a signature context used for signing (not yet implemented).
  """

  # place of/for '?'
  url = str(url) # might be unicode
  qi = url.find('?')
  if qi < 0: qi = len(url)
  params = dict()
  if relay_state: params['RelayState'] = relay_state
  sig = message.get_signature_request()
  if sig is not None:
    # Note: we must ensure ``message.Destination`` is set
    message.Destination = url[:qi]
    # cancel the signature request
    message.clear_signature_request()
    params["SigAlg"] = config.signature_method
  # ``compress`` does not really implements the deflate algorithm as of RFC1951
  #   but adds a 2 byte header and a 4 byte trailor (which we remove)
  msg = compress(message.toxml(root_only=True))[2:-4].encode('base64')
  # remove whitespace
  msg = ''.join(msg.split())
  params[isinstance(message, ResponseType) and 'SAMLResponse' or 'SAMLRequest'] \
                             = msg
  qs = urlencode(params)
  if qi == len(url): url += '?' # '?' not yet present
  if qi != len(url)-1 and not url.endswith('&'): url += '&'
  url += urlencode(params)
  if sig is not None:
    data = parse_for_signature(url)
    url += "&" + urlencode(dict(
      Signature="".join(sig.sign_binary(message, data).encode("base64").split())
      ))
  return url


def decode(url, context=None):
  """decode *url* and return pair *saml* and *relay_state*.

  *url* is the complete url, including the query string (necessary
  for signature verification).

  *context* is used for signature verification (not yet implemented).

  Note: if a signature is present, the returned *saml* is a `PyXM`
  object, otherwise a `str`.
  """
  qs = url[url.index('?')+1:]
  params = parse_qs(qs) # maps param to list of values
  relay_state = params.get('RelayState')
  if relay_state is not None: relay_state = relay_state[0] # unlistify
  msg = (params.get('SAMLRequest') or params.get('SAMLResponse'))[0]
  # Note: RPC 1951 implies an unwrapped deflated data stream
  #  call ``decompress`` with a negative second argument to
  #  specify this case.
  msg = decompress(msg.decode("base64"), -15)
  if 'Signature' in params:
    __traceback_info__ = msg # a Zope thing, but it does not hurt
    from ..pyxb.protocol import CreateFromDocument
    # will raise exceptions if signature verifications fail
    m = CreateFromDocument(msg)
    data = parse_for_signature(url)
    if context is None:
      from ..signature import default_verify_context
      context = default_verify_context
    # will raise an exception, if the verification fails
    keyname = m.S_GET_KEYNAME()
    context.verify_binary(
      data,
      params["SigAlg"][0],
      params["Signature"][0].decode("base64"),
      keyname
      )
    m.set_signature_verification(keyname)
    return m, relay_state
  return msg, relay_state  


def parse_for_signature(url):
  qs = url[url.index("?")+1:]
  qd = dict((qa[:qa.index("=")], qa) for qa in qs.split("&") if "=" in qa)
  return "&".join(qd[k] for k
                  in ("SAMLRequest", "SAMLResponse", "RelayState", "SigAlg")
                  if qd.get(k)
                  )
