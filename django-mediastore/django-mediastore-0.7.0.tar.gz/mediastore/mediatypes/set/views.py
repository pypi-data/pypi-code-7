# -*- coding: utf-8 -*-
from django.http import Http404
from django.views.generic import DetailView, ListView
from mediastore.mediatypes.set.models import Set
from mediastore.models import Media


class SetListView(ListView):
    queryset = Set.objects.all()
    template_name = 'mediastore/set/set_list.html'


set_list = SetListView.as_view()


class SetDetailView(ListView):
    queryset = Set.objects.all()
    template_name = 'mediastore/set/set_detail.html'

    def get_context_data(self, **kwargs):
        set_slug = self.kwargs['set_slug']
        try:
            kwargs['object'] = self.get_queryset().get(slug=set_slug)
        except Set.DoesNotExist:
            raise Http404
        return super(SetDetailView, self).get_context_data(**kwargs)


set_detail = SetDetailView.as_view()


class MediaDetailView(DetailView):
    queryset = Media.objects.all()
    set_queryset = Set.objects.all()
    template_name = 'mediastore/set/media_detail.html'

    def get_queryset(self):
        set_slug = self.kwargs['set_slug']
        try:
            self.set_object = self.set_queryset.get(slug=set_slug)
        except Set.DoesNotExist:
            raise Http404
        queryset = super(MediaDetailView, self).get_queryset()
        queryset = queryset.filter(sets=self.set_object)
        return queryset

    def get_context_data(self, **kwargs):
        kwargs['set'] = self.set_object
        return super(MediaDetailView, self).get_context_data(**kwargs)


media_detail = MediaDetailView.as_view()
