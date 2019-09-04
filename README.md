# buildly

A gateway and service discovery system for “micro” services. A light weight Gateway that connects all of your data services, API’s and endpoints to a single easy-to-use URL.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

* Docker version 19+

### Installing

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

## Deployment

Add additional notes about how to deploy this on a live system and preference for [Humanitec](https://humanitec.com) and Walhall.

### Configure the API authentication

All clients interact with our API using the OAuth2 protocol. In order to
configure it, go to `admin/oauth2_provider/application/` and add a new
application there.

### Generating RSA keys

For using JWT as authentication method, we need to configure public and
private RSA keys.

The following commands will generate a public and private key. The private
key will stay in Buildly and the public one will be supplied to
microservices in order to verify the authenticity of the message:

```bash
$ openssl genrsa -out private.pem 2048
$ openssl rsa -in private.pem -outform PEM -pubout -out public.pem
```

### Configuration

The following table lists the configurable parameters of buildly and their default values.

|             Parameter               |            Description             |                    Default                |
|-------------------------------------|------------------------------------|-------------------------------------------|
| `ALLOWED_HOSTS`                     | A list of strings representing the domain names the app can serve  | `[]`      |
| `CORS_ORIGIN_WHITELIST`             | A list of origins that are authorized to make cross-site HTTP requests  | `[]` |
| `DATABASE_ENGINE`                   | The database backend to use. (`postgresql`, `mysql`, `sqlite3` or `oracle`) | `` |
| `DATABASE_NAME`                     | The name of the database to use          | ``                                  |
| `DATABASE_USER`                     | The username to use when connecting to the database | ``                       |
| `DATABASE_PASSWORD`                 | The password to use when connecting to the database | ``                       |
| `DATABASE_HOST`                     | The host to use when connecting to the database | ``                           |
| `DATABASE_PORT`                     | The port to use when connecting to the database | ``                           |
| `DEFAULT_ORG`                       | The first organization created in the database  | `My Organization`            |
| `JWT_ISSUER`                        | The name of the JWT issuer               | ``                                  |
| `JWT_PRIVATE_KEY_RSA_BUILDLY`       | The private RSA KEY                      | ``                                  |
| `JWT_PUBLIC_KEY_RSA_BUILDLY`        | The public RSA KEY                       | ``                                  |
| `SOCIAL_AUTH_GITHUB_REDIRECT_URL`   | The redirect URL for GitHub Social auth  | None                                |
| `SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URL`  | The redirect URL for Google Social auth  | None                          |
| `SOCIAL_AUTH_LOGIN_REDIRECT_URL`    | Redirect the user once the auth process ended successfully | None                              |
| `SOCIAL_AUTH_MICROSOFT_GRAPH_REDIRECT_URL` | The redirect URL for Microsoft graph Social auth | None                 |
| `ACCESS_TOKEN_EXPIRE_SECONDS`       | The number of seconds an access token remains valid | None                                |
| `SECRET_KEY`                        | Used to provide cryptographic signing, and should be set to a unique, unpredictable value | None |
| `OAUTH_CLIENT_ID`                   | Used in combination with OAUTH_CLIENT_SECRET to create OAuth2 password grant | None |
| `OAUTH_CLIENT_SECRET`               | Used in combination with OAUTH_CLIENT_ID to create OAuth2 password grant | None |
| `USE_PASSWORD_MINIMUM_LENGTH_VALIDATOR`   | If true, checks whether the password meets a minimum length | None       |
| `PASSWORD_MINIMUM_LENGTH`           | The minimum length of passwords      | `6` |
| `USE_PASSWORD_USER_ATTRIBUTE_SIMILARITY_VALIDATOR`  | If true, checks the similarity between the password and a set of attributes of the user | None |
| `USE_PASSWORD_COMMON_VALIDATOR`     | If true, checks whether the password occurs in a list of common passwords | None |
| `USE_PASSWORD_NUMERIC_VALIDATOR`    | If true, checks whether the password isn’t entirely numeric | None |

Specify each parameter using `-e`, `--env`, and `--env-file` flags to set simple (non-array) environment variables to `docker run`. For example,

```bash
$ docker run -e MYVAR1 --env MYVAR2=foo \
    --env-file ./env.list \
    ubuntu bash
```

## Built With

* [Drone](http://www.drone.io) - Recommended CI/CD

## Contributing

Please read [CONTRIBUTING.md](https://github.com/buildlyio/docs/CONTRIBUTING) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).

## Authors

* **Buildly** - *Initial work*

See also the list of [contributors](https://github.com/buidlyio/buildly/contributors) who participated in this project.

## License

This project is licensed under the GPL v3 License - see the [LICENSE.md](LICENSE.md) file for details
