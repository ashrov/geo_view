from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def search_view(request: HttpRequest) -> HttpResponse:
    """View для отображения главной страницы веб-приложения."""
    return render(
        request,
        'search.html',
    )
