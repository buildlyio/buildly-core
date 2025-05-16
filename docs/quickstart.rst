.. _quickstart:

Quickstart
==========

This is an introduction to Buildly's Core. 

Prerequisites
----------

Docker version 19+

Buildly Core repo
----------

Fork or clone the repository 

https://github.com/buildlyio/buildly-core


Setting up Buildly Core
----------
Make sure you have docker up and running then build the image:

.. code-block:: bash
   
   docker compose build # --no-cache to force dependencies installation

Next run the web server: 

.. code-block:: bash
   
   docker compose up # -d for detached

Access the web server at http://127.0.0.1:8080

User: `admin`
Password: `admin`.

To run the web server with Python debugger support:

.. code-block:: bash
   
   docker compose run --rm --service-ports buildly

Configuring the API authentication
--------------------------------



Generating RSA keys
-------------------

To use JSON Web Token as the authentication method, you will need to configure public and private RSA keys.

To generate the public and private keys run the following commands: 

.. code-block:: bash
   
   openssl genrsa -out private.pem 2048
   openssl rsa -in private.pem -outform PEM -pubout -out public.pem
   
*The private key will stay in Buildly and the public one will be supplied to your microservices in order to verify the authenticity of the message.*

Running the tests
-----------------

To run the tests (without flake8) and have Python debugger open on error:

.. code-block:: bash
   
   docker compose run --entrypoint '/usr/bin/env' --rm buildly bash scripts/run-tests.sh --keepdb

To run the tests with flake8:

.. code-block:: bash
   
   docker compose run --entrypoint '/usr/bin/env' --rm buildly bash scripts/run-tests.sh --ci

For more tesing options enter:

.. code-block:: bash

    pytest --help
