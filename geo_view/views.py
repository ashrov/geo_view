from dataclasses import dataclass
from datetime import date
from typing import Any

from django.conf import settings
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from pydantic import BaseModel, ValidationError, field_validator

from geo_view import __version__
from geo_view.management.commands.process_locations import ProcessWorker
from geo_view.models import GeoPosition, Location


def get_global_context(_: HttpRequest) -> dict:
    return {
        'version': __version__,
    }


@dataclass
class SearchStat:
    """Статистика запроса поиска."""

    articles_count: int
    positions_count: int
    articles_shown: int = 0


class SearchOptions(BaseModel):
    """Параметры поиска."""

    start: date | None = None
    end: date | None = None
    place: str = ''
    limit: int | None = None

    @field_validator('start', 'end', mode='before')
    @classmethod
    def validate_datetime(cls, value: Any) -> date | None:
        """Валидатор для даты, в который может прийти пустая строка, её надо обработать как `None`."""
        if not value:
            return None
        return date.fromisoformat(value)

    @field_validator('place')
    @classmethod
    def validate_place(cls, value: str) -> str:
        if value and not GeoPosition.objects.filter(name=value).first():
            msg = f'No such place for "{value}"'
            raise ValueError(msg)

        return value

    @property
    def as_query(self) -> str:
        """Представление параметров в виде query для url."""
        return '&'.join(
            f'{field}={value}'
            for field, value in self.model_dump(
                mode='json',
                exclude_defaults=True,
            ).items()
        )

    def get_positions(self) -> tuple[SearchStat, list[Location]]:
        """Получение позиций по параметрам."""
        locations = Location.objects.all()
        if self.start:
            locations = locations.filter(article__date__gte=self.start)
        if self.end:
            locations = locations.filter(article__date__lt=self.end)
        if self.place:
            children = GeoPosition.get_all_children(self.place)
            locations = locations.filter(position__in=children)

        raw_stat = locations.aggregate(
            positions_count=Count('position_id', distinct=True),
            articles_count=Count('article_id', distinct=True),
        )
        stat = SearchStat(**raw_stat)

        locations = locations[:(self.limit or settings.POSITIONS_DISPLAY_LIMIT)]
        locations_list = list(locations.prefetch_related('article', 'position'))
        stat.articles_shown = len(locations_list)
        return stat, locations_list


def search_view(request: HttpRequest) -> HttpResponse:
    """View для отображения главной страницы веб-приложения."""
    if request.method == 'POST':
        try:
            options = SearchOptions(**request.POST.dict())
        except ValidationError as er:
            errors = [f'{error["loc"][0]}: {error["msg"]}' for error in er.errors()]
            return render(
                request,
                'search.html',
                context={
                    'errors': errors,
                },
            )
        else:
            return redirect(
                f'/map/?{options.as_query}',
            )

    return render(
        request,
        'search.html',
    )


def map_view(request: HttpRequest) -> HttpResponse:
    """View для отображения карты."""
    options = SearchOptions(**request.GET.dict())
    stat, locations = options.get_positions()

    return render(
        request,
        'map.html',
        context={
            'stat': stat,
            'locations': locations,
        },
    )


def coords_view(request: HttpRequest) -> HttpResponse:
    """View для отображения страницы поиска места."""
    loc = {}
    if request.method == 'GET':
        loc = ProcessWorker().get_nominatim_info(request.GET.dict().get('name', '')) or {}

    return render(
        request,
        'coords.html',
        context=loc,
    )
