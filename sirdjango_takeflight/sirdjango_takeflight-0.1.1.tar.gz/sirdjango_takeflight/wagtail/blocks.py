from sirdjango.blocks import BaseBlock

from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.six import text_type

from wagtail.wagtailcore.templatetags.wagtailcore_tags import richtext
from wagtail.wagtailimages.models import get_image_model, Filter, SourceImageIOError


path_prefix = 'sirdjango_takeflight/wagtail/'


class FullwidthImageBlock(BaseBlock):
    name = 'FullwidthImageBlock'
    filter_spec = 'max-165x165'
    template = path_prefix + 'fullwidthimage.html'

    class Media:
        js = [path_prefix + 'js/fullwidthimage.js']

    def clean(self, data):
        # May still exist if the image was not changed
        data.pop('image_tag', None)

        if set(data.keys()) != {'image_id'}:
            raise ValidationError('Invalid data for {0} block'.format(self.name))

        Image = get_image_model()
        try:
            image = Image.objects.get(pk=data['image_id'])
        except Image.DoesNotExist:
            raise ValidationError('Image does not exist')

        filter, _ = Filter.objects.get_or_create(spec=self.filter_spec)
        try:
            rendition = image.get_rendition(filter)
        except SourceImageIOError:
            Rendition = image.renditions.model
            rendition = Rendition(image=image, width=0, height=0)
            rendition.file.name = 'not-found'

        image_tag = rendition.img_tag({'data-image-tag': True})
        data['image_tag'] = text_type(image_tag)

        return data

    def render_json(self, data):
        Image = get_image_model()
        try:
            image = Image.objects.filter(pk=data['image_id']).get()
        except Image.DoesNotExist:
            return ''
        context = data.copy()
        context.update({
            'image': image,
        })
        return render_to_string(self.template, context)


class Text(BaseBlock):
    name = 'Text'

    class Media:
        js = [path_prefix + 'js/hallo.js']

    def clean(self, data):
        if set(data.keys()) != {'html'}:
            raise ValidationError('Invalid data for {0} block'.format(self.name))
        return data

    def render_json(self, data):
        return richtext(data['html'])
