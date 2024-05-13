from datetime import datetime
from itertools import batched
from pathlib import Path

from corus.sources.lenta import load_lenta
from django.core.management import BaseCommand, CommandParser
from django.db import transaction

from geo_view.models import Article


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('--news-file', required=True, type=Path)
        parser.add_argument('--batch-size', default=10000, type=int)

    @transaction.atomic(savepoint=False)
    def handle(self, *_, news_file: Path, batch_size: int, **__) -> None:
        news = load_lenta(news_file)

        Article.objects.all().delete()

        for articles in batched(news, batch_size):
            to_create = [
                Article(
                    url=article.url,
                    title=article.title,
                    text=article.text,
                    topic=article.topic,
                    tags=article.tags,
                    date=datetime.strptime(article.date, '%Y/%m/%d'),
                )
                for article in articles
            ]
            Article.objects.bulk_create(to_create, ignore_conflicts=True)
