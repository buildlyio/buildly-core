# BiFrost - Humanitec Platform Core Service

[![Build Status](http://drone.humanitec.io/api/badges/Humanitec/bifrost/status.svg)](http://drone.humanitec.io/Humanitec/bifrost)

**Documentation page: [\_index.md](_index.md)**

The partner front end service for BiFrost is [Midgard (Angular) and Midgard Core]:https://github.com/Humanitec/midgard and is configured to connect to the BiFrost core automatically and facilitate connections to addtional platform frontend and backend services.

## Deploy locally via Docker

Build first the images:

```bash
docker-compose build # --no-cache to force deps installation
```

To run the webserver (go to 127.0.0.1:8080):

```bash
docker-compose up # -d for detached
```

User: `admin`
Password: `admin`.

To run the webserver with pdb support:

```bash
docker-compose run --rm --service-ports bifrost
```

To run bash:

```bash
docker-compose run --entrypoint '/usr/bin/env' --rm bifrost bash
```

or if you initialized already a container:

```bash
docker exec -it bifrost bash
```

To connect to the database when the container is running:

```bash
docker exec -it postgres_bifrost psql -U root bifrost
```

If the database is empty, you may want to populate extra demo data to play
around:

```bash
docker-compose run --entrypoint 'python manage.py loadinitialdata --demo' bifrost
```

Or if you want to restore the demo data keeping the users:

```bash
docker-compose run --entrypoint 'python manage.py loadinitialdata --restore' bifrost
```

If you would like to clean the database and start the application, do:

```bash
docker-compose up --renew-anon-volumes --force-recreate --build
```


### Tests

To run the tests (without flake8) and have `ipdb` open on error:

```bash
docker-compose run --entrypoint '/usr/bin/env' --rm bifrost bash scripts/run-tests.sh --keepdb --bash_on_finish
```

To run the tests like if it was CI with flake8:

```bash
docker-compose run --entrypoint '/usr/bin/env' --rm bifrost bash scripts/run-tests.sh --ci
```

See `pytest --help` for more options.

## Set up

### First steps

1. Create a superuser: `python manage.py createsuperuser`
2. Add basic data: `python manage.py loadinitialdata`


### Configure the API authentication

All clients interact with our API using the OAuth2 protocol. In order to
configure it, go to `admin/oauth2_provider/application/` and add a new
application there.


### Configure Elasticsearch (search function)

Search Function is configured through connected search service.
https://github.com/humanitec/search_service


### Configure other services

There are many other services and behaviours determined by the
application's configuration. Revise `bifrost/settings/base.py` and
configure your environment variables so all services work without failures.

### Generating RSA keys

For using JWT as authentication method, we need to configure public and
private RSA keys.

The following commands will generate a public and private key. The private
key will stay in BiFrost and the public one will be supplied to
microservices in order to verify the authenticity of the message:

```bash
$ openssl genrsa -out private.pem 2048
$ openssl rsa -in private.pem -outform PEM -pubout -out public.pem
```


## Troubleshooting

### Local environment problems

If you're getting an error in your local environment, it can be related to the
social-core library. To solve this issue you need to execute the following
step:

- With the container running, go into it with this command:

  `docker-compose run --entrypoint '/usr/bin/env' --rm bifrost bash`

- Install the `social-core` lib again:

  `pip install -e git://github.com/toladata/social-core#egg=social-core`

- Restart the container to apply the changes.

## Creating PRs and Issues
The following templates were created to easy the way to create tickets and help the developer.

- Bugs and Issues [[+]](https://github.com/Humanitec/bifrost/issues/new)
- New features [[+]](https://github.com/Humanitec/bifrost/issues/new?template=new_features.md)
- Pull requests [[+]](https://github.com/Humanitec/bifrost/compare/master?expand=1)

Use the following template to create tickets for E-Mail:
```
From: [email_address]
To: [email_address]
Cc: [email_address]
Bcc: [email_address]
Reply-to: [email_address]

Subject: 'Title'
Body: 'Text message'(HTML)
```
