
from rest_framework import serializers
from django_eulasees import models


class RawEulaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RawEula

class EulaSnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EulaSnippet

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag

class TagIconSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TagIcon

class TagEulaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TagEula

class SnippetTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SnippetTag


        
