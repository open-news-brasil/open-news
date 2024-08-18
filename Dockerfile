FROM --platform=amd64 python:3.11-alpine3.20

COPY scrapy.cfg /srv
COPY pyproject.toml /srv
COPY noticias_phb /srv/noticias_phb

WORKDIR /srv

RUN apk update && \
    apk add gcc g++ python3-dev musl-dev linux-headers alpine-conf && \
    setup-timezone /America/Sao_Paulo && \
    pip install --upgrade pip poetry psutil && \
    poetry install --without dev

ENV CRON_EXPRESSION '*/10 * * * *'
ENV CRON_COMMAND 'cd /srv; poetry run task scrape'

RUN echo "$CRON_EXPRESSION $CRON_COMMAND" >> /var/spool/cron/crontabs/root
RUN echo "0 0 * * * rm /srv/noticias_phb.log" >> /var/spool/cron/crontabs/root

CMD [ "crond", "-f" ]
