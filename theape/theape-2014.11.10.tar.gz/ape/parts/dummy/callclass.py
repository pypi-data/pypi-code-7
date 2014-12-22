
# this package
from ape import BaseClass
from ape import ARGS, KWARGS


class CallClass(BaseClass):
    """
    A class for dummies to return when called.
    """
    def __init__(self, message=None, payload=None):
        """
        CallClass constructor

        :param:

          - `message`: string to return from __str__
          - `payload`: payload to return on call
        """
        super(CallClass, self).__init__()
        if message is None:
            message = 'call'
        self.message = message

        self.payload = payload
        return

    def __call__(self, *args, **kwargs):
        """
        returns the payload after logging items
        """
        self.logger.info(ARGS.format(value=args))
        self.logger.info(KWARGS.format(value=kwargs))
        return self.payload

    def __str__(self):
        """
        Returns the name given
        """
        return self.message
