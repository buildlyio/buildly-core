# Quickstart

Excited to get start? This page gives a decent prologue to Buildly Core. It assumes 
you as of now have Docker installed.

## Installing

Build first the image:

```bash
docker-compose build # --no-cache to force dependencies installation
```

To run the webserver (go to 127.0.0.1:8080):

```bash
docker-compose up # -d for detached
```

User: `admin`
Password: `admin`.

To run the webserver with pdb support:

```bash
docker-compose run --rm --service-ports buildly
```

## Configure the API authentication

All clients interact with our API using the OAuth2 protocol. In order to configure it, go to 
`admin/oauth2_provider/application/` and add a new application there.

## Generating RSA keys

For using JWT as authentication method, we need to configure public and private RSA keys.

The following commands will generate a public and private key. The private key will stay in Buildly and the public 
one will be supplied to microservices in order to verify the authenticity of the message:

```bash
$ openssl genrsa -out private.pem 2048
$ openssl rsa -in private.pem -outform PEM -pubout -out public.pem
```

## Running the tests

To run the tests (without flake8) and have `ipdb` open on error:

```bash
docker-compose run --entrypoint '/usr/bin/env' --rm buildly bash scripts/run-tests.sh --keepdb --bash_on_finish
```

To run the tests like if it was CI with flake8:

```bash
docker-compose run --entrypoint '/usr/bin/env' --rm buildly bash scripts/run-tests.sh --ci
```

See `pytest --help` for more options.
