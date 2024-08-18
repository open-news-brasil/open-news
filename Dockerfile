FROM --platform=amd64 python:3.11-alpine3.19

COPY scrapy.cfg /srv
COPY pyproject.toml /srv
COPY requirements.txt /srv
COPY noticias_phb /srv/noticias_phb

WORKDIR /srv

RUN apk update && \
    apk add gcc py3-scikit-learn musl-dev linux-headers alpine-conf && \
    setup-timezone /America/Sao_Paulo && \
    pip install --upgrade pip psutil && \
    pip install -r requirements.txt

ENV CRON_EXPRESSION '*/10 * * * *'
ENV CRON_COMMAND 'cd /srv; task scrape'
ENV PYTHONPATH '/usr/lib/python3.11/site-packages'

RUN echo "$CRON_EXPRESSION $CRON_COMMAND" >> /var/spool/cron/crontabs/root
RUN echo "0 0 * * * rm /srv/noticias_phb.log" >> /var/spool/cron/crontabs/root

CMD [ "crond", "-f" ]
