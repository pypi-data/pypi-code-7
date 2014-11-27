from plone.app.layout.viewlets import ViewletBase
from Products.CMFCore.utils import getToolByName

class LastModifiedViewlet(ViewletBase):

    def modified(self):
        return self.toLocalizedTime(self.context.ModificationDate(), True)

    def toLocalizedTime(self, time, long_format=None, time_only=None):
        """Convert time to localized time
        """
        util = getToolByName(self.context, 'translation_service')
        return util.ulocalized_time(time, long_format, time_only, self.context,
                                    domain='plonelocales')
