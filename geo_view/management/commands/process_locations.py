from collections.abc import Iterator
from functools import lru_cache
from multiprocessing.pool import Pool
from pathlib import Path
from typing import NamedTuple

import django
from natasha import NewsEmbedding, NewsNERTagger
from natasha.morph.tagger import NewsMorphTagger
from natasha.morph.vocab import MorphForm, CACHE_SIZE

try:
    django.setup()
except RuntimeError:
    pass

import requests
from django.core.cache import cache
from django.core.management import BaseCommand, CommandParser
from django.db import connections, transaction
from django.db.models import Count
from pymorphy3 import MorphAnalyzer
from natasha import LOC, Segmenter, Doc
from geo_view.models import Article, GeoPosition


class MorphVocab(MorphAnalyzer):
    def __init__(self):
        MorphAnalyzer.__init__(self, result_type=MorphForm)

    parse = lru_cache(CACHE_SIZE)(MorphAnalyzer.parse)
    __call__ = parse

    def __repr__(self) -> str:
        return self.__class__.__name__

    def lemmatize(self, word, pos, feats):
        from natasha.morph.lemma import lemmatize

        return lemmatize(self, word, pos, feats)


class Worker:
    def __init__(self, nerus_file: Path, nominatim_url: str) -> None:
        self._nerus_file = nerus_file
        self._nominatim_url = nominatim_url
        self._morph_vocab = MorphVocab()

        self._segmenter = Segmenter()

        embedding = NewsEmbedding()
        self._ner_tagger = NewsNERTagger(embedding)
        self._morph_tagger = NewsMorphTagger(embedding)

    def process(self) -> None:
        connections.close_all()
        with Pool() as pool:
            tasks = (
                Article.objects.annotate(pos_count=Count('geo_positions'))
                .filter(pos_count=0).only('text').iterator()
            )

            # for _ in pool.imap_unordered(self.process_article, tasks):
            #     pass
            for task in tasks:
                self.process_article(task)

    @transaction.atomic(savepoint=False)
    def process_article(self, article: Article) -> None:
        for quote, normal_form in self.get_locations(article):
            cache_key = normal_form.replace(' ', '_')
            result = cache.get(cache_key)
            if result is None:
                with requests.get(f'{self._nominatim_url}?q={normal_form}', timeout=120) as response:
                    results = response.json()
                    if results:
                        result = results[0]
                        cache.set(cache_key, result)
                    else:
                        cache.set(cache_key, '')

            if result:
                GeoPosition(
                    article=article,
                    name=result['display_name'],
                    quote=quote,
                    lat=result['lat'],
                    lon=result['lon'],
                ).save()

    def get_locations(self, article: Article) -> Iterator[tuple[str, str]]:
        doc = Doc(article.text)

        doc.segment(self._segmenter)
        doc.tag_morph(self._morph_tagger)
        doc.tag_ner(self._ner_tagger)
        for span in doc.spans:
            span.normalize(self._morph_vocab)

        for span in doc.spans:
            if span.type == LOC:
                yield span.text, span.normal


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('--nerus-file', required=True, type=Path)
        parser.add_argument('--nominatim-url', required=True, type=str)

    def handle(self, *_, nerus_file: Path, nominatim_url: str, **__) -> None:
        worker = Worker(nerus_file, nominatim_url)
        worker.process()
