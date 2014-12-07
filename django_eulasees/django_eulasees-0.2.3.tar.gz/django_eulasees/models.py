# -*- coding: utf-8 -*-
from django.contrib import admin
from django.db import models

class RawEula(models.Model):
    """ The raw text EULA """
    description = models.CharField(max_length=100)
    site = models.CharField(max_length=100)
    text = models.TextField()
    url = models.CharField(max_length=200)
    date = models.DateField()
    #version
    #owner

    def __str__(self):
        """ Use the site """
        return self.description

class EulaSnippet(models.Model):

    title = models.CharField(max_length=200)
    eula = models.ForeignKey(RawEula)
    text = models.TextField()
    def __str__(self):

        return self.title


class Tag(models.Model):
    """ A property that might apply to multiple EULA's"""
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):

        return self.name
    

class SnippetTag(models.Model):

    tag = models.ForeignKey(Tag)
    snippet = models.ForeignKey(EulaSnippet)

    def __str__(self):

        return "%s/%s" % (str(self.tag), str(self.snippet))


class TagIcon(models.Model):
    """ Associated an Icon with a tag

    Icon is just name of a file in static/img
    """
    tag = models.ForeignKey(Tag)
    icon = models.CharField(max_length=200)

class TagEula(models.Model):
    """ Associated another EULA with a tag

    Some EULA's are annoying and reference other documents.

    So, use this to associated another EULA with a tag.

    For example, suppose the foo.com EULA references the foo.com privacy
    policy.

    Create a new EULA object for the privacy policy.

    Then tag the paragraph that mentions the privacy policy with the foo.com
    privacy policy tag and create a TagEula object for that tag that
    references both the privacy policy RawEula object and the privacy policy tag. 
    """
    tag = models.ForeignKey(Tag)
    eula = models.ForeignKey(RawEula)
    

# admin site stuff
admin.site.register(RawEula)
admin.site.register(EulaSnippet)
admin.site.register(Tag)
admin.site.register(SnippetTag)
admin.site.register(TagIcon)
admin.site.register(TagEula)


