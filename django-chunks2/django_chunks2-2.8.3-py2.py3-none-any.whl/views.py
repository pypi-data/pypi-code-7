# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseNotModified
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from .forms import EditForm
from .models import Chunk


def edit_view(request, key):
    obj = get_object_or_404(Chunk, key=key)
    form = EditForm(request.POST or None, instance=obj)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return HttpResponse('')
        else:
            return HttpResponseNotModified('')
    return render(
        request, 'chunks/editform.html', {'form': form, 'key': key})
