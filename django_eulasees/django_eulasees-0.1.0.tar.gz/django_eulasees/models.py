# -*- coding: utf-8 -*-
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

class EulaSnippet(models.Model):

    title = models.CharField(max_length=200)
    eula = models.ForeignKey(RawEula)
    text = models.TextField()

class SnippetData(models.Model):
    pass


class Tag(models.Model):
    """ A property that might apply to multiple EULA's"""
    name = models.CharField(max_length=50)
    description = models.TextField()

class SnippetTag(models.Model):

    tag = models.ForeignKey(Tag)
    tag = models.ForeignKey(EulaSnippet)
    





