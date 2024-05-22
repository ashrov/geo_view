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
from geo_view.models import GeoPosition


def get_global_context(_: HttpRequest) -> dict:
    return {
        'version': __version__,
    }


@dataclass
class SearchStat:
    articles_count: int
    positions_count: int
    shown_count: int = 0


class SearchOptions(BaseModel):
    start: date | None = None
    end: date | None = None
    limit: int | None = None

    @field_validator('start', 'end', mode='before')
    @classmethod
    def validate_datetime(cls, value: Any) -> date | None:
        if not value:
            return None
        return date.fromisoformat(value)

    @property
    def as_query(self) -> str:
        return '&'.join(
            f'{field}={value}'
            for field, value in self.model_dump(
                mode='json',
                exclude_defaults=True,
            ).items()
        )

    def get_positions(self) -> tuple[SearchStat, list[GeoPosition]]:
        positions = GeoPosition.objects.all()
        if self.start:
            positions = positions.filter(article__date__gte=self.start)
        if self.end:
            positions = positions.filter(article__date__lt=self.end)

        raw_stat = positions.aggregate(positions_count=Count('id'), articles_count=Count('article_id', distinct=True))
        stat = SearchStat(**raw_stat)

        positions = positions[:(self.limit or settings.POSITIONS_DISPLAY_LIMIT)]
        positions_list = list(positions)
        stat.shown_count = len(positions_list)
        return stat, positions_list


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
    stat, positions = options.get_positions()

    return render(
        request,
        'map.html',
        context={
            'stat': stat,
            'positions': positions,
        },
    )


def coords_view(request: HttpRequest) -> HttpResponse:
    loc = {}
    if request.method == 'GET':
        loc = ProcessWorker().get_nominatim_info(request.GET.dict().get('name', '')) or {}

    return render(
        request,
        'coords.html',
        context=loc,
    )
