# GeoView
[![Поддерживаемые Python версии](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Поддерживаемые Python версии](https://img.shields.io/badge/Django-5.0-green.svg)](https://www.djangoproject.com/)
[![Поддерживаемые Python версии](https://img.shields.io/badge/psycopg-3.1-orange.svg)](https://www.psycopg.org/)
[![Качество кода](https://api.codacy.com/project/badge/Grade/63cae098e6d943d5ba6519da82a79636)](https://app.codacy.com/gh/kkozoriz/geo_view/dashboard)

Веб приложение для визуализации мест из новостей с сайта lenta.ru

## Запуск в докере

```shell
docker-compose -f docker/docker-compose.yml up --build
```

Для запуска импорта новостей в базу данных
необходимо запустить docker-compose с профилем `import`

```shell
docker-compose --profile import -f docker/docker-compose.yml up --build
```
## Дополнительное

### Линтер и анализатор типов
***
В проект добавлен линтер `ruff` и анализатор `mypy`.

Установка:

```shell
pip install -e ".[tests]"
```

Запуск проверок:

```shell
ruff check
mypy --install-types --non-interactive
```
