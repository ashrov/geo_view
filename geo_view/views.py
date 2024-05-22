from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def search_view(request: HttpRequest) -> HttpResponse:
    """View для отображения главной страницы веб-приложения."""
    return render(
        request,
        'search.html',
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
