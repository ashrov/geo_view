from datetime import date
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from pydantic import BaseModel, ValidationError, field_validator

from geo_view.models import GeoPosition


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
        return '&'.join(f'{field}={value}' for field, value in self.model_dump(mode='json', exclude_defaults=True).items())

    def get_positions(self) -> list[GeoPosition]:
        postions = GeoPosition.objects.all()
        if self.start:
            postions = postions.filter(article__date__gte=self.start)
        if self.end:
            postions = postions.filter(article__date__lt=self.start)
        if self.limit:
            postions = postions[:self.limit]
        return list(postions)


def search_view(request: HttpRequest) -> HttpResponse:
    """View для отображения главной страницы веб-приложения."""
    options = SearchOptions()

    if request.method == 'POST':
        try:
            options = SearchOptions(**request.POST.dict())
        except ValidationError as er:
            errors = [f'{error["loc"][0]}: {error["msg"]}' for error in er.errors()]
            return render(
                request,
                'search.html',
                context={'options': options, 'errors': errors},
            )

        return redirect(
            f'/map/?{options.as_query}',
        )

    return render(
        request,
        'search.html',
        context={'options': options},
    )


def map_view(request: HttpRequest) -> HttpResponse:
    """View для отображения карты."""
    options = SearchOptions(**request.GET.dict())

    return render(
        request,
        'map.html',
        context={
            'positions': options.get_positions(),
        },
    )
