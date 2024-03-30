FROM tiangolo/uwsgi-nginx-flask:python3.8

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        nano \
    && rm -rf /var/lib/apt/lists/*

ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static

COPY ./requirements.txt /var/www/requirements.txt

RUN python -m pip install --upgrade pip && \
    pip install -r /var/www/requirements.txt
