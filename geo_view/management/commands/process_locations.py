from collections.abc import Iterator
from functools import lru_cache
from typing import Any

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.management import BaseCommand
from django.db import models, transaction
from natasha import LOC, Doc, NewsEmbedding, NewsNERTagger, Segmenter
from natasha.morph.tagger import NewsMorphTagger
from natasha.morph.vocab import CACHE_SIZE, MorphForm
from pymorphy3 import MorphAnalyzer

from geo_view.models import Article, GeoPosition


class MorphVocab(MorphAnalyzer):
    def __init__(self) -> None:
        MorphAnalyzer.__init__(self, result_type=MorphForm)

    parse = lru_cache(CACHE_SIZE)(MorphAnalyzer.parse)
    __call__ = parse

    def __repr__(self) -> str:
        return self.__class__.__name__

    def lemmatize(self, word: Any, pos: Any, feats: Any) -> Any:
        from natasha.morph.lemma import lemmatize

        return lemmatize(self, word, pos, feats)


class ProcessWorker:
    def __init__(self) -> None:
        self._nominatim_url = settings.NOMINATIM_URL
        self._morph_vocab = MorphVocab()

        self._segmenter = Segmenter()

        embedding = NewsEmbedding()
        self._ner_tagger = NewsNERTagger(embedding)
        self._morph_tagger = NewsMorphTagger(embedding)

    def process(self) -> None:
        articles = (
            Article.objects.annotate(pos_count=models.Count('geo_positions'))
            .filter(pos_count=0).only('text').iterator()
        )

        for article in articles:
            self.process_article(article)

    @transaction.atomic(savepoint=False)
    def process_article(self, article: Article) -> None:
        for quote, normal_form in self.get_locations(article):
            result = self.get_nominatim_info(normal_form)

            if result:
                GeoPosition(
                    article=article,
                    name=result['display_name'],
                    quote=quote,
                    lat=result['lat'],
                    lon=result['lon'],
                ).save()

    def get_nominatim_info(self, loc: str) -> dict | None:
        cache_key = loc.replace(' ', '_')
        result = cache.get(cache_key)
        if result is not None:
            return result

        if result == '':
            return None

        with requests.get(f'{self._nominatim_url}?q={loc}', timeout=120) as response:
            results = response.json()

        if results:
            cache.set(cache_key, results[0])
            return results[0]

        cache.set(cache_key, '')
        return None

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
    def handle(self, *_, **__) -> None:
        worker = ProcessWorker()
        worker.process()
