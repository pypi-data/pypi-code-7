import os
from django.views.generic import TemplateView
from django.http import Http404

# Create your views here.
class SongBirdView(TemplateView):
    prefix = ""
    def get_template_names(self):
        path = "{}.html".format(
            self.kwargs['path'].rstrip('/') or 'index')
        if not os.path.exists(path):
            raise Http404
        return [os.path.join(self.prefix, path + ".html")]
