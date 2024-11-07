from django.contrib import admin
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = 'pk', 'title', 'content', 'pub_date', 'author', 'category',
