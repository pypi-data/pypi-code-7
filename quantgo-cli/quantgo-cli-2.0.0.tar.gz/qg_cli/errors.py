# ======================= QuantGo Copyright Notice ============================
# Copyright 2013 QuantGo, LLC.  All rights reserved.
# Permission to use solely inside a QuantGo Virtual Quant Lab
# Written By: Nikolay
# Date: 12-12.2013
# ======================= QuantGo Copyright Notice ============================

class BaseClientError(Exception): pass
class InvalidAction(BaseClientError): pass
class ServerError(BaseClientError): pass
class InvalidParameter(BaseClientError): pass
