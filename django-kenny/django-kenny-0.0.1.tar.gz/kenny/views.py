import os
from django.views.generic import TemplateView

# Create your views here.
class SongBirdView(TemplateView):
    prefix = ""
    def get_template_names(self):
        path = self.kwargs['path'].rstrip('/') or 'index'
        return [os.path.join(self.prefix, path + ".html")]
