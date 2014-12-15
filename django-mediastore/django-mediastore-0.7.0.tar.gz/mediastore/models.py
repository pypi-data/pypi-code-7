# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _
from taggit.managers import TaggableManager
from .utils.managers import InheritanceManager, InheritanceQuerySet
from .utils import is_media_instance


_media_type_registry = {}
_content_type_to_model_cache = {}


class MediaQuerySet(InheritanceQuerySet):
    def type(self, obj):
        '''
        Filter queryset by media type. First arguments needs to be either a
        model, a model instance or the model._meta.object_name of a Media
        subclass.
        '''
        media_type = None
        # if obj is a string then let's see what the registry knows about it
        if obj in _media_type_registry:
            obj = _media_type_registry[obj]
        try:
            if issubclass(obj, Media):
                media_type = ContentType.objects.get_for_model(obj)
        except TypeError:
            if isinstance(obj, Media):
                media_type = obj.content_type
        if media_type is None:
            raise ValueError('Cannot determine media type from %r' % obj)
        return self.filter(content_type=media_type)

    def list_by_type(self):
        '''
        Will evaluate the queryset.
        '''
        types = {}
        for obj in self.select_subclasses():
            if obj.media_type not in types:
                types[obj.media_type] = []
            types[obj.media_type].append(obj)
        return types


class MediaManager(InheritanceManager):
    def get_queryset(self):
        return MediaQuerySet(self.model)

    def type(self, obj):
        return self.get_queryset().type(obj)

    def list_by_type(self):
        return self.get_queryset().list_by_type()


class Media(models.Model):
    media_type = None
    help_text = None
    icon = None

    # details
    name = models.CharField(max_length=120, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True, help_text=_(
        u'Leave this field blank for autopopulating a unique tag '
        u'based on the objects name.'
    ))

    # categorization
    tags = TaggableManager(blank=True)
    content_type = models.ForeignKey(ContentType, editable=False)

    created = models.DateTimeField(auto_now_add=True)

    # managers
    objects = MediaManager()

    class Meta:
        app_label = 'mediastore'
        verbose_name = _('media')
        verbose_name_plural = _('media')
        ordering = ('created',)

    def __repr__(self):
        name = 'Media'
        if self.__class__ is not Media:
            name = 'Media:%s' % self.__class__.__name__
        return '<%s: pk=%d "%s">' % (name, self.pk, self.name or '')

    def __unicode__(self):
        return self.name or u''

    def get_media_type(self):
        if self.media_type:
            return self.media_type
        return self.content_type.model_class().media_type

    def generate_slug(self):
        from mediastore.utils import unique_slug
        return unique_slug(self.name or self.pk, Media)

    def save(self, *args, **kwargs):
        if self.content_type_id is None:
            media_content_type = ContentType.objects.get_for_model(Media)
            content_type = ContentType.objects.get_for_model(self)
            if content_type != media_content_type:
                self.content_type = content_type
        if not self.content_type:
            raise AssertionError('''This media instance has no associated media type. Access Media only by subclasses.''')
        if not self.slug:
            self.slug = self.generate_slug()
        super(Media, self).save(*args, **kwargs)

    @property
    def object(self):
        '''
        Returns the related media item.
        '''
        if not hasattr(self, '_related_media_instance'):
            self._related_media_instance = None
            if is_media_instance(self):
                self._related_media_instance = self
            else:
                model = self.content_type.model_class()
                o2o_rel = model._meta.get_field_by_name('media_ptr')[0]
                attname = o2o_rel.related_query_name()
                self._related_media_instance = getattr(self, attname)
        return self._related_media_instance


def assign_media_types(sender, **kwargs):
    if issubclass(sender, Media):
        if getattr(sender, 'media_type', None) is None:
            sender.media_type = sender._meta.object_name.lower()
        if sender.media_type in _media_type_registry:
            raise AssertionError(
                u'There is already a registered media type "%s"' % sender.media_type)
        _media_type_registry[sender.media_type] = sender

signals.class_prepared.connect(
    assign_media_types,
    dispatch_uid='mediastore.models.assign_media_types')
