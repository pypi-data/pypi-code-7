from django.db import models
#from django.utils import translation
#from django.conf import settings
#from django.http import Http404#,HttpResponse
#from django.template import Context, Template
#from django.shortcuts import render
#from django.shortcuts import render_to_response
#from django.core.urlresolvers import reverse

import tinycms


class MenuItem(models.Model):
    """Page menu

    Variables:
    page -- Foreign key for page
    language -- Language of this content
    title -- title to be shown in menu
    """
    page = models.ForeignKey(tinycms.models.Page, related_name='menuitem')
    language = models.CharField(max_length=256, choices=tinycms.models.LANGUAGES)
    title = models.CharField(max_length=1024)

    def __unicode__(self):
        return unicode(self.page)+":"+unicode(self.title)+":"+unicode(self.language)

    def getTitle(self):
        """Return title
        """
        return self.title


