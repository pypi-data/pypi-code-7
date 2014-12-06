# coding=utf-8
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from easy_thumbnails.files import get_thumbnailer
from image_cropping import ImageRatioField



try:
    fotorama_crop_size = settings.FOTORAMA_CROP_SIZE
except AttributeError:
    fotorama_crop_size = '600x300'


class MainSliderManager(models.Manager):
    def get_queryset(self):
        # Добавим фильтр по дате публикации
        import datetime
        from django.db.models import Q
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        return super(MainSliderManager, self).get_queryset().filter(
            Q(pub_start__gte=today, pub_end__lt=tomorrow) |
            Q(pub_start=None, pub_end__lt=tomorrow) |
            Q(pub_start__gte=today, pub_end=None) |
            Q(pub_start=None, pub_end=None)
        )


class FotoramaSlider(models.Model):

    def generate_order(self):
        no = FotoramaSlider.objects.count()
        if no == None:
            return 1
        else:
            return no + 1

    def get_dir_name(self, filename):
        import uuid
        _end = filename.split('.')[-1]
        name = str(uuid.uuid4())[0:8]
        return u'image/content/gallery/{}_{}.{}'.format(self.pk, name, _end)

    name = models.CharField(_(u'Заголовок слайда'), max_length=50, null=True, blank=False)

    query = models.CharField(_(u'uri запроса'), max_length=70,
        help_text=_(u'Адрес запроса http://domain.ru/<<uri запроса>>'), null=True, blank=False
    )

    image = models.ImageField(_(u'изображение'), upload_to=get_dir_name)
    cropping = ImageRatioField('image', fotorama_crop_size, verbose_name=_(u'обрезка изображения'))
    order = models.IntegerField(_(u'приоритет слайда'), default=generate_order)

    pub_start = models.DateField(_(u'Дата начала публикации'), null=True, blank=True, help_text=_(u'Оставьте пустым, для снятия ограничения'))
    pub_end = models.DateField(_(u'Дата конца публикации'), null=True, blank=True, help_text=_(u'Оставьте пустым, для снятия ограничения'))

    created = models.DateTimeField(u'Создание', auto_now_add=True)
    modify = models.DateTimeField(u'Изменение', auto_now=True)

    admin_objects = models.Manager()
    objects = MainSliderManager()

    def admin_img(self):
        if self.avatar:
            try:
                thumbnail_url = get_thumbnailer(self.avatar).get_thumbnail({
                    'size': (50, 50),
                    # 'box': self.cropping,
                    #'crop': True,
                    'detail': True,
                }).url
            except:
                return 'Broken Img'
            return u'<img src="%s" />' % thumbnail_url
        else:
            return '(Does not exists)'

    admin_img.short_description = _(u'слайд')
    admin_img.allow_tags = True

    def __unicode__(self):
        return u'{name}'.format(name=self.name or 'slide #%d' % self.pk)

    class Meta:
        ordering = ['-order', 'created']
        verbose_name = _(u'слайд')
        verbose_name_plural = _(u'слайды')
