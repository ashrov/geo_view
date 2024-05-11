from collections.abc import Iterator, Iterable
from pathlib import Path
from typing import NamedTuple
from itertools import batched

from django.conf import settings
from corus.sources.lenta import load_lenta, LentaRecord
from tqdm import tqdm
from nerus import load_nerus, NerusDoc, NERMarkup

from .models import Article

CREATE_BATCH_SIZE = 1000


class Coordinates(NamedTuple):
    lat: float
    lon: float


cache: dict[str, Coordinates] = {}


def load_articles() -> None:
    news = load_lenta(settings.LENTA_NEWS_PATH)

    for articles in batched(news, CREATE_BATCH_SIZE):
        to_create = [
            Article(
                url=article.url,
                title=article.title,
                text=article.text,
                topic=article.topic,
                tags=article.tags,
                date=article.date,
            )
            for article in articles
        ]
        Article.objects.bulk_create(to_create, ignore_conflicts=True)


def process_nerus_doc(markup: NERMarkup) -> None:
    text = markup.text
    locs = [
        text[tag.start:tag.stop]
        for tag in markup.spans
        if tag.type == 'LOC'
    ]

    article = Article(
        text=text
    )


