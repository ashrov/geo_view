FROM python:3.12

WORKDIR app
COPY pyproject.toml .
COPY geo_view/__init__.py geo_view/__init__.py
RUN pip install . && pip uninstall -y geo-view

COPY . .
RUN pip install . && rm -rf /app

WORKDIR /

ENV DJANGO_SETTINGS_MODULE="geo_view.settings"
