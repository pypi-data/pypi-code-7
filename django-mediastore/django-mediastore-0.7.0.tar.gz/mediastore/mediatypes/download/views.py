# -*- coding: utf-8 -*-
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from mediastore.mediatypes.download.models import Download


def download_counter(request, slug, filename=None):
    download = get_object_or_404(Download, slug=slug)
    Download.objects.filter(pk=download.pk).update(count=F('count') + 1)
    return HttpResponseRedirect(download.file.url)
