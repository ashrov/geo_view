FROM python:3.12

WORKDIR app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD python manage.py migrate && python manage.py runserver 0.0.0.0:8000
