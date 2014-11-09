# coding: utf-8

from django.core.cache import cache
from django.db import models
from django.utils.translation import ugettext_lazy as _


class TemplateZone(models.Model):
    name = models.CharField(_('Zone name'), max_length=255)
    description = models.TextField(
        _('Short description'), blank=True)

    class Meta:
        verbose_name = _('Template zone')
        verbose_name_plural = _('Template zones')

    def __unicode__(self):
        return '%s - %s' % (self.name, self.description)

    def save(self, *args, **kwargs):
        """Save and invalidate zone cache."""
        super(TemplateZone, self).save(*args, **kwargs)
        cache.delete('cmstemplates:%s' % self.name)


class TemplateFile(models.Model):
    name = models.CharField(
        _('Template name'),
        max_length=255,
        help_text=_('Template name, for example, "headline"'),
    )
    zone = models.ForeignKey(
        TemplateZone, verbose_name=_('Zone'), related_name='files')
    weight = models.IntegerField(_('Output order'), default=0)
    template_filename = models.CharField(
        _('Template file name'), max_length=500, blank=True)
    use_content = models.BooleanField(
        _('Use template text'), default=False)
    template_content = models.TextField(
        _('Template text'), blank=True)
    is_active = models.BooleanField(_('Active'), default=True)
    only_for_superuser = models.BooleanField(
        _('Only for superuser'), default=False)

    class Meta:
        verbose_name = _('Template file')
        verbose_name_plural = _('Template files')
        ordering = ['weight']

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Save and invalidate zone cache."""
        super(TemplateFile, self).save(*args, **kwargs)
        cache.delete('cmstemplates:%s' % self.zone.name)

    def source_path(self):
        """Represents template source, used by admin site."""
        if not self.use_content:
            return self.template_filename
        return _('template text')
    source_path.short_description = _('Source')
