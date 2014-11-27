from django.views.generic.detail import DetailView


class ContentDetailView(DetailView):
    context_object_name = 'content'
    template_name = 'content/content.html'


class ArticleDetailView(ContentDetailView):
    template_name = 'content/article.html'

    def get_queryset(self):
        q = super().get_queryset()
        q = q.filter(
            publication_time__year=self.kwargs['year'],
            publication_time__month=self.kwargs['month'],
            publication_time__day=self.kwargs['day'],
        )
        return q
