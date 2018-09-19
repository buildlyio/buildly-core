FROM python:2.7

COPY . /code
WORKDIR /code

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install nginx -y

ADD docker/etc/nginx/bifrost-api.conf /etc/nginx/conf.d/bifrost-api.conf

RUN pip install -r requirements/production.txt

# Collecting static files
# RUN ./collectstatic.sh

EXPOSE 8080

ARG BRANCH=None
ENV branch=${BRANCH}

ENTRYPOINT ["/code/docker-entrypoint.sh"]
