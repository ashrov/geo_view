from __future__ import annotations

from collections.abc import Iterable
from typing import Self

from django.db import models
from django.db.models import Count


class Article(models.Model):
    url = models.TextField(default='')
    title = models.TextField(default='')
    text = models.TextField(default='')
    topic = models.TextField(default='', db_index=True)
    tags = models.TextField(default='', db_index=True)
    date = models.DateField(db_index=True)
    processed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'Article {self.url} {self.title} {self.date}'


class GeoPosition(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, related_name='children', db_index=True)
    name = models.TextField(db_index=True)
    display_name = models.TextField()
    lat = models.FloatField(null=True)
    lon = models.FloatField(null=True)

    class Meta:
        unique_together = (('parent', 'name'),)

    def __str__(self) -> str:
        return f'GeoPosition "{self.name}", lat: {self.lat}, lon: {self.lon}'

    @classmethod
    def get_by_full_name(cls, name: str, *, lat: float, lon: float) -> Self:
        path = name.split(', ')
        current: cls | None = None

        for i, loc in enumerate(reversed(path), start=1):
            display_name = ', '.join(path[-i:])
            current, _ = cls.objects.get_or_create(name=loc, parent=current, defaults={'display_name': display_name})

        current.lat = lat
        current.lon = lon
        current.display_name = name
        current.save()

        return current

    @classmethod
    def get_all_children(cls, name: str) -> Iterable[Self]:
        start = cls.objects.filter(name=name)
        result: set[GeoPosition] = set(start)
        last: set[GeoPosition] = set(result)

        while True:
            last = set(cls.objects.filter(parent__in=last))
            result.update(last)

            if not last:
                return result

    @classmethod
    def clean_up(cls) -> None:
        cls.objects.annotate(
            locations_count=Count('locations'),
            children_count=Count('children'),
        ).filter(
            locations_count=0,
            children_count=0,
        ).delete()


class Location(models.Model):
    quote = models.TextField()
    position = models.ForeignKey(GeoPosition, on_delete=models.CASCADE, related_name='locations', db_index=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='locations', db_index=True)

    def __str__(self) -> str:
        return f'Location "{self.quote}" with position "{self.position.name}"'
