# coding: utf-8

from django.core.cache import cache
from django.db import models
from django.utils.translation import ugettext_lazy as _


class TemplateGroup(models.Model):
    name = models.CharField(_('Template group name'), max_length=255)
    description = models.TextField(
        _('Short description'), blank=True)

    class Meta:
        verbose_name = _('Template group')
        verbose_name_plural = _('Template groups')

    def __unicode__(self):
        if self.description:
            return '%s - %s' % (self.name, self.description)
        return self.name

    def save(self, *args, **kwargs):
        """Save and invalidate template group cache."""
        super(TemplateGroup, self).save(*args, **kwargs)
        cache.delete('cmstemplates:group:%s' % self.name)


class Template(models.Model):
    name = models.CharField(
        _('Template name'),
        max_length=255,
        help_text=_('Template name, for example, "headline"'),
    )
    group = models.ForeignKey(
        TemplateGroup,
        verbose_name=_('Group'),
        related_name='templates',
    )
    # TODO: add help text in which order output works
    weight = models.IntegerField(_('Output order'), default=0)
    content = models.TextField(_('Content'))
    is_active = models.BooleanField(_('Active'), default=True)
    only_for_superuser = models.BooleanField(
        _('Only for superuser'), default=False)

    class Meta:
        verbose_name = _('Template')
        verbose_name_plural = _('Template')
        ordering = ['weight']

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Save and invalidate group cache."""
        super(Template, self).save(*args, **kwargs)
        cache.delete('cmstemplates:group:%s' % self.group.name)
