from django.contrib.sitemaps import Sitemap
from django.db.models import Prefetch
from .models import Article, Tag


class BlogSitemap(Sitemap):
    changefreq = 'never'
    priority = 0.5

    def items(self):
        return Article.objects.defer('content').select_related('author', 'category').prefetch_related(
            Prefetch('tags', queryset=Tag.objects.only('name'))
        ).order_by('-pub_date')

    def lastmod(self, obj: Article):
        return obj.pub_date


