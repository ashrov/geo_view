from django.contrib import admin

from .models import Article, GeoPosition


@admin.register(Article)
class Admin(admin.ModelAdmin):
    list_fields = ('title', 'url', 'text', 'topic', 'tags')
    list_filter = ('topic', 'tags')
    search_fields = ('url=', 'title', 'text')


@admin.register(GeoPosition)
class GeoPositionAdmin(admin.ModelAdmin):
    list_fields = ('name', 'quote', 'lat', 'lon', 'article')
    search_fields = ('name', 'quote')
