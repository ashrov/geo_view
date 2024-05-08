from django.contrib import admin

from .models import Article, GeoPosition


@admin.register(Article)
class Admin(admin.ModelAdmin):
    pass


@admin.register(GeoPosition)
class GeoPositionAdmin(admin.ModelAdmin):
    pass
