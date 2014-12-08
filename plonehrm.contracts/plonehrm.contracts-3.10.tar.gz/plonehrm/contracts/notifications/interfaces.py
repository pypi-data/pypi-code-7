from plonehrm.notifications.interfaces import IHRMModuleEvent
from plonehrm.notifications.interfaces import IHRMEmailer


class IContractEvent(IHRMModuleEvent):
    pass


class IContractEmailer(IHRMEmailer):
    pass
