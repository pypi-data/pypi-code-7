from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from .utils import unique_slugify

from django.db import models


class LinkItem(models.Model):

    parent = models.ForeignKey('self', blank=True, null=True)
    display_name = models.CharField(_("Display Name"), max_length=255,
                                    blank=False)

    txtid = models.CharField(_('txtid'), max_length=255, unique=True)
    order = models.PositiveIntegerField('Order', null=True,
                                        help_text="Order in which this\
                                        link appears in the set.")

    path = models.CharField(_('path'), max_length=255)

    url = models.CharField(_("URL"), max_length=255, blank=True,
                           help_text="Enter the full path for an external\
                           link, i.e. http://www.website.com or relative \
                           path for internal link, i.e. /login/")
    hide = models.BooleanField(_("Hide from LinkSet"), default=False)

    def save(self, *args, **kwargs):

        self.path = self.generate_path()

        unique_slugify(self, self.display_name, 'txtid')

        # Dont let link item point to self
        if self.parent and self.parent == self:
            self.parent = None

        super(LinkItem, self).save(*args, **kwargs)

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "display_name__icontains",
                "parent__display_name")

    @property
    def admin_levels(self):
        if self.parent:
            return "%s<span style='color:#fff'>|------</span>"
            % self.parent.admin_levels
        else:
            return ""

    @property
    def admin_title(self):
        if self.parent:
            return mark_safe("%s&lfloor; %s"
                             % (self.admin_levels, self.display_name))
        else:
            return self.display_name

    def generate_path(self):
        if self.parent:
            return "%s%s/%s/" % (self.parent.path, self.order, self.txtid)
        else:
            return "/%s/" % self.txtid

    class Meta:
        ordering = ['order']
        verbose_name = "Link Item"
        verbose_name_plural = "Link Items"

    def __unicode__(self):
        return self.display_name

    def get_children(self):
        return self.__class__.objects.filter(parent=self)\
            .exclude(hide=True).order_by('order')

    def get_path(self):
        if self.url:
            return self.url

    def get_target(self):
        if self.url:
            if 'http' in self.url:
                return 'target=_blank'
            else:
                return ''
        else:
            return ''
