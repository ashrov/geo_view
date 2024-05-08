from collections.abc import Iterator
from pathlib import Path

from corus.sources.lenta import load_lenta, LentaRecord


def get_news(path: Path) -> Iterator[LentaRecord]:
    load_lenta(path)
