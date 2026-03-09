from django.contrib import admin

from .models import NewsArticle, NewsImpact


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'published_at')
    list_filter = ('source',)

@admin.register(NewsImpact)
class NewsImpactAdmin(admin.ModelAdmin):
    list_display = ('article', 'instrument', 'sentiment')