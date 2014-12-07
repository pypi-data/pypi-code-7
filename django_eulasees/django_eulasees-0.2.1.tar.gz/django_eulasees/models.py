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
        return self.site

class EulaSnippet(models.Model):

    title = models.CharField(max_length=200)
    eula = models.ForeignKey(RawEula)
    text = models.TextField()
    start = models.PositiveIntegerField(blank=True)
    end = models.PositiveIntegerField(blank=True)

class SnippetData(models.Model):
    pass


class Tag(models.Model):
    """ A property that might apply to multiple EULA's"""
    name = models.CharField(max_length=50)
    description = models.TextField()

class SnippetTag(models.Model):

    tag = models.ForeignKey(Tag)
    snippet = models.ForeignKey(EulaSnippet)

# admin site stuff
admin.site.register(RawEula)
admin.site.register(EulaSnippet)
admin.site.register(Tag)
admin.site.register(SnippetTag)








