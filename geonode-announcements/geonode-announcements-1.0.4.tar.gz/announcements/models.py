from django.db import models
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

# support custom user models in django 1.5+
# https://docs.djangoproject.com/en/1.5/topics/auth/customizing/#substituting-a-custom-user-model
try:
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
else:
    User = get_user_model()

class AnnouncementType(models.Model):
    identifier = models.CharField(max_length=255, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    severity = models.PositiveSmallIntegerField(null=True, default=0,help_text=_('A positive integer representing the severity of the announcement.  The severity increases as the value increases.'))
    urgency = models.PositiveSmallIntegerField(null=True, default=0,help_text=_('A positive integer respresenting the urgency of the announcement.  The urgency increases as the value increases.'))

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ("-severity","-urgency",)
        verbose_name_plural = _("Announcement Types")

class Announcement(models.Model):
    """
    A single announcement.
    """
    DISMISSAL_NO = 1
    DISMISSAL_SESSION = 2
    DISMISSAL_PERMANENT = 3
    
    DISMISSAL_CHOICES = [
        (DISMISSAL_NO, _("No Dismissals Allowed")),
        (DISMISSAL_SESSION, _("Session Only Dismissal")),
        (DISMISSAL_PERMANENT, _("Permanent Dismissal Allowed"))
    ]
    
    title = models.CharField(_("title"), max_length=50)
    type = models.ForeignKey(AnnouncementType, null=True, blank=True)
    content = models.TextField(_("content"))
    creator = models.ForeignKey(User, verbose_name=_("creator"))
    creation_date = models.DateTimeField(_("creation_date"), default=timezone.now)
    site_wide = models.BooleanField(_("site wide"), default=False)
    members_only = models.BooleanField(_("members only"), default=False)
    dismissal_type = models.IntegerField(choices=DISMISSAL_CHOICES, default=DISMISSAL_SESSION)
    publish_start = models.DateTimeField(_("publish_start"), default=timezone.now)
    publish_end = models.DateTimeField(_("publish_end"), blank=True, null=True)
    
    def get_absolute_url(self):
        return reverse("announcements_detail", args=[self.pk])
    
    def dismiss_url(self):
        if self.dismissal_type != Announcement.DISMISSAL_NO:
            return reverse("announcements_dismiss", args=[self.pk])
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name = _("announcement")
        verbose_name_plural = _("announcements")


class Dismissal(models.Model):
    user = models.ForeignKey(User, related_name="announcement_dismissals")
    announcement = models.ForeignKey(Announcement, related_name="dismissals")
    dismissed_at = models.DateTimeField(default=timezone.now)
