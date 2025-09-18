FROM python:3.10.18-alpine3.22
LABEL authors="akostenikov@gmail.com"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR app/

COPY requirements.txt requirements.txt
RUN apk add --no-cache build-base musl-dev libffi-dev postgresql-dev jpeg-dev zlib-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del build-base musl-dev libffi-dev postgresql-dev jpeg-dev zlib-dev

COPY . .

RUN mkdir -p /files/static \
    && adduser -D -H my_user \
    && chown -R my_user /files/static \
    && chmod -R 755 /files/static

USER my_user
