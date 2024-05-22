from datetime import datetime
from typing import Literal, Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from pydantic import BaseModel, ValidationError, Field, field_validator


class SearchOptions(BaseModel):
    start: datetime | None = None
    end: datetime | None = None

    @field_validator('start', 'end', mode='before')
    @classmethod
    def validate_datetime(cls, value: Any) -> datetime | None:
        if not value:
            return None
        return datetime.fromisoformat(value)

    @property
    def as_query(self) -> str:
        return '&'.join(f'{field}={value}' for field, value in self.model_dump(mode='json', exclude_defaults=True).items())


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
    return render(
        request,
        'map.html',
        context={
            'positions': [
                (10.1, 20.1),
            ],
        },
    )
