FROM python:3.6

WORKDIR /code

# Install tcp-port-wait.sh requirements
RUN apt-get update && apt-get install -y netcat

# NginX config
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install nginx -y

ADD docker/etc/nginx/bifrost-api.conf /etc/nginx/conf.d/bifrost-api.conf

COPY ./requirements/base.txt requirements/base.txt
COPY ./requirements/production.txt requirements/production.txt
RUN pip install -r requirements/production.txt

ADD . /code

EXPOSE 8080
ENTRYPOINT ["bash", "/code/docker-entrypoint.sh"]
