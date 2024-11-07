from django.db.models import Prefetch
from django.shortcuts import render
from django.contrib.syndication.views import Feed
from django.views.generic import ListView, DetailView
from django.urls import reverse, reverse_lazy

from blogapp.models import Article, Tag


class ArticleListView(ListView):
    model = Article
    template_name = 'blogapp/article_list.html'
    context_object_name = 'article_list'
    queryset = Article.objects.defer('content').select_related('author', 'category').prefetch_related(
        Prefetch('tags', queryset=Tag.objects.only('name'))
    ).order_by('-pub_date')


class ArticleDetailView(DetailView):
    model = Article


class LatestArticlesFeed(Feed):
    title = "Blog articles (latest)"
    description = "Updates on changes and additions to blog articles"
    link = reverse_lazy("blogapp:article_list")

    def items(self):
        return (
            Article.objects.defer('content').select_related('author', 'category').prefetch_related(
                Prefetch('tags', queryset=Tag.objects.only('name'))
            ).order_by('-pub_date')[:5]
        )

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.content[:200]
