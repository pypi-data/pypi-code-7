
from rest_framework import serializers
from django_eulasees import models


class RawEulaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.RawEula

class EulaSnippetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.EulaSnippet

class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Tag

class TagIconSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.TagIcon

class TagEulaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.TagEula

class SnippetTagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.SnippetTag


        
