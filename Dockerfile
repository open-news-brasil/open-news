FROM --platform=amd64 python:3.12-alpine3.20

COPY scrapy.cfg /srv
COPY pyproject.toml /srv
COPY requirements.txt /srv
COPY open_news /srv/open_news

WORKDIR /srv

RUN apk update && \
    apk add gcc py3-scikit-learn musl-dev linux-headers alpine-conf && \
    setup-timezone /America/Sao_Paulo && \
    pip install --upgrade pip psutil && \
    pip install -r requirements.txt

ENV CRON_EXPRESSION '*/10 * * * *'
ENV CRON_COMMAND 'cd /srv; task scrape'
ENV PYTHONPATH '/usr/lib/python3.12/site-packages'

RUN echo "$CRON_EXPRESSION $CRON_COMMAND" >> /var/spool/cron/crontabs/root
RUN echo "0 0 * * * rm /srv/open_news.log" >> /var/spool/cron/crontabs/root

CMD [ "crond", "-f" ]
