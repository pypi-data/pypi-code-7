# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>; see 'LICENSE.txt' for details
"""Configuration - for signing/verification (at the moment).

This module is designed for monkey patching: An application
which wants non default settings overrides the variables defined
in this module during startup.
"""

############################################################################
# What we are using when generating signatures
signature_method = "http://www.w3.org/2000/09/xmldsig#rsa-sha1"
canonicalization_method = "http://www.w3.org/2001/10/xml-exc-c14n#"
digest_method = "http://www.w3.org/2000/09/xmldsig#sha1"



############################################################################
# What we are accepting for verification
#  We automatically add the exclusive canonicalization methods (with and
#  without comment) and the enveloped transform
from dm.xmlsec.binding import \
     TransformRsaSha1, TransformRsaSha256, \
     TransformSha1, TransformSha256 

signature_transforms = TransformRsaSha1, TransformRsaSha256,
reference_transforms = TransformSha1, TransformSha256, 
