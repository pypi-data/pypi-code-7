from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _
from facebook import display_album

from models import FacebookGallery


class FacebookGalleryPlugin(CMSPluginBase):
    model = FacebookGallery
    name = _("Facebook Album Gallery")
    render_template = "cmsplugin_fbgallery/album.html"

    def render(self, context, instance, placeholder):
        album = display_album(instance.album_id)
        context.update({
            'object': instance,
            'album': album,
        })
        return context

plugin_pool.register_plugin(FacebookGalleryPlugin)
