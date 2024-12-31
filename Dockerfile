FROM python:3.8

# Do not buffer log messages in memory; some messages can be lost otherwise
ENV PYTHONUNBUFFERED 1

# Install the project requirements.
COPY requirements.txt /
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

WORKDIR /code

ADD . /code

# Collecting static files
RUN ./scripts/collectstatic.sh

# Specify tag name to be created on github
LABEL version="1.0.10"

EXPOSE 8080
ENTRYPOINT ["bash", "/code/scripts/docker-entrypoint.sh"]

# Specify tag name to be created on github
LABEL version="1.0.0"