# GeoView

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


