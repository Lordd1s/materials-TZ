FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV PYTHONPATH=/usr/local

COPY ./app /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-root --only main

WORKDIR /app/app
CMD python manage.py migrate && python manage.py collectstatic --noinput && gunicorn settings.wsgi:application --workers=1 --bind 0.0.0.0:8000
EXPOSE 8000
