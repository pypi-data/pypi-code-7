# -*- coding: utf-8 -*-

from django import forms
from .models import Chunk


class EditForm(forms.ModelForm):
    class Meta:
        model = Chunk
        fields = ('id', 'content', )
