from __future__ import annotations

from django.db import models


class Article(models.Model):
    url = models.TextField(default='')
    title = models.TextField(default='')
    text = models.TextField(default='')
    topic = models.TextField(default='')
    tags = models.TextField(default='')
    date = models.DateField(null=True)

    def __str__(self) -> str:
        return f'Article {self.title} {self.date}'


class GeoPosition(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='geo_positions')
    name = models.TextField()
    lat = models.FloatField()
    lon = models.FloatField()

    def __str__(self) -> str:
        return f'GeoPosition "{self.name}", lat: {self.lat}, lon: {self.lon}'
