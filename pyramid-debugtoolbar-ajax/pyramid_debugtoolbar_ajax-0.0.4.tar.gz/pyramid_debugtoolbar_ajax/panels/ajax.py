from pyramid_debugtoolbar.panels import DebugPanel


_ = lambda x: x


class AjaxDebugPanel(DebugPanel):
    """
    Sample debug panel
    """
    name = 'Ajax'
    has_content = True
    template = 'pyramid_debugtoolbar_ajax.panels:templates/ajax.dbtmako'

    def __init__(self, request):
        self.data = data = {'request': request}

    @property
    def nav_title(self):
        return _(self.name)

    @property
    def title(self):
        return _(self.name)

    @property
    def url(self):
        return ''

    def render_content(self, request):
        self.data['toolbar_request'] = request
        return DebugPanel.render_content(self, request)
