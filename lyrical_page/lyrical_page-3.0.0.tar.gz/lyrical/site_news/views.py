from django.views.generic import ListView, DetailView
from django.http import Http404

from lyrical.site_news.models import SiteNewsArticle, SiteNewsCategory


class IndexListView(ListView):
    model = SiteNewsArticle
    template_name = 'site_news/index_list.html'
    context_object_name = 'sitenewsarticles'


class ArticleDetailView(DetailView):
    model = SiteNewsArticle
    template_name = 'site_news/article_detail.html'
    context_object_name = 'sitenewsarticle'

    def get_object(self, queryset=None):
        """
        Returns the object the view is displaying.
        By default this requires `self.queryset` and a `pk` or `slug` argument
        in the URLconf, but subclasses can override this to return any object.
        """
        
        try:
            obj = SiteNewsArticle.objects.get(sitenewscategory__url=self.kwargs.get('sitenewscategory'),
                                              url=self.kwargs.get('sitenewsarticle'))
        except SiteNewsArticle.DoesNotExist:
            raise Http404('No article found')
        
        return obj
