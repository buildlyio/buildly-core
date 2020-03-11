.. _connect service to buildly:

Connect your service to Buildly
===============================

Overview
--------

This tutorial explains how to connect an existing service to `Buildly <https://buildly.io/buildly-core/>`_. 

Once you connect your service to Buildly, it will be able to communicate with all of your other services over a core authentication layer. All of its endpoints will be exposed as part of a single API that Buildly puts together from all of the services. You also have the option to use Buildly for managing permissions and users.

Requirements
------------

There are no requirements for the language or framework used to code your service. It must only satisfy these conditions in order to connect to Buildly:

1.  Your service must follow the `OpenAPI (Swagger) spec <https://swagger.io/docs/specification/about/>`_.
2.  You need to expose a `swagger.json` file at the `/docs` endpoint.
3.  Your service must use an `OAuth2 <https://oauth.net/2/>`_ library with support for `JSON Web Tokens (JWTs) <https://jwt.io>`_. See the `Implement JWT authorization`_ section for more information.

Implement JWT authorization
---------------------------

Next, you need to implement Buildly's authorization method. 

About Buildly authorization
^^^^^^^^^^^^^^^^^^^^^^^^^^^

For external requests to modules (e.g., `Buildly UI <https://github.com/buildlyio/buildly-ui-angular>`_ users), Buildly uses an `OAuth2 <https://oauth.net/2/>`_ flow to issue `JSON Web Tokens (JWTs) <https://jwt.io>`_ signed with RS256. 

Buildly's **public key** should be exposed as the environment variable `JWT_PUBLIC_KEY_RSA_BUILDLY` inside the container where the service is deployed. The service must use this environment variable to decode requests from Buildly. 

Buildly passes the JWT to the service in the `Authorization` HTTP header using the format `JWT {token}`. Example:

.. code-block:: bash

   Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJiaWZyb3N0IiwiZXhwIjoxNTYwNjA0OTc2LCJpYXQiOjE1NjA1MTg1NzYsImNvcmVfdXNlcl91dWlkIjoiODJiZGI2YTMtMjExOS00MThmLThjMmQtY2FhYjdlYmI4OTc1Iiwib3JnYW5pemF0aW9uX3V1aWQiOiJiMjY1YmFkNS1iODEyLTRmNDItYjNlZS0zNDFlYmJiNzJjNmIiLCJzY29wZSI6InJlYWQgd3JpdGUiLCJ1c2VybmFtZSI6ImFkbWluIn0.CV8PafWuGDZSpWRI5wC6btO6cyt9udI9P5uLBdnHzVhbbIY-LH1o3qBgnRf0OAreUhRfl7zBTBMNO56pbyWeyg

Example using PyJwt
^^^^^^^^^^^^^^^^^^^

Here's an example using the `PyJwt library <https://pyjwt.readthedocs.io/en/latest/>`_. It takes the `encoded_jwt` from the HTTP header and decodes it with the `JWT_PUBLIC_KEY_RSA_BUILDLY` environment variable:

.. code-block:: python
   
   import jwt

   jwt.decode(encoded_jwt, os.environ['JWT_PUBLIC_KEY_RSA_BUILDLY'], algorithms=['RS256'])


The Buildly JWT payload looks like this:

.. code-block::
   
   {
	   "core_user_uuid": "fd76ce0c-d8be-4aa6-91ed-59e698f6af60",
	   "exp": 1560472728,
	   "iat": 1560436728,
	   "iss": "buildly",
	   "organization_uuid": "70f0d039-e3d9-427e-b161-4e95dbd9e918",
	   "scope": "read write",
	   "username": "admin"
   }


-  `core_user_uuid`: UUID of the [CoreUser](/model/permissions#coreuser) who initiated the request.
-  `exp`: Datetime when the token expires.
-  `iat`: Datetime when the token was issued.
-  `iss`: Issuer of the JWT. This will always be `buildly`.
-  `organization_uuid`: UUID of the [Organization](/model/permissions#organization) that contains the CoreUser who initiated the request.
-  `scope`: Permission scopes granted in the request by Buildly.
-  `username`: The username of the CoreUser who initiated the request.

Add Your Service to Buildly 
---------------------------

After finishing the JWT authorization implementation, deploying your service somewhere and exposing it externally, you need to add it to Buildly.

To add your service to Buildly, make sure it meets the prerequisites, then navigate to the Buildly admin page at `https://<YOUR-BUILDLY-URL>/admin` and log into it. Then, under the section **Core** you will see **Logic Module**, click on it and add a new one with the following properties:

- Name: The name of your service for identification
- Endpoint: The host of your microservice e.g. https://my-amazing-service.com
- Endpoint Name: The API endpoint for your service (just type the name of the endpoint, for example, `amazing`

Now, your service will be accessed by Buildly and exposed following the structure `https://<BUILDLY-URL>/api/<ENDPOINT-NAME>`, so our service example above will be accessable via the URL `https://<YOUR-BUILDLY-URL>/api/amazing`.

To verify that this has worked, navigate to the Buildly docs at `https://<YOUR-BUILDLY-URL>/docs` and you should see the Swagger documentation for your service under Buildly’s documentation.

(Optional) Implement Buildly permissions model
----------------------------------------------

If you want to implement the Buildly :ref:`permissions model` in your services, then you need to create **WorkflowLevels** for each of your data models and implement them in the models. We recommend creating WorkflowLevel1s for all top-level data models in your service and WorkflowLevel2s for defining any nested data relationships.

Use the following endpoints of your **app's API URL** to define WorkflowLevels:

-  POST /workflowlevel1: Create WorkflowLevel1
	-  Add the property `workflowleve1_uuid` to the data model and set the value to the UUID from the response.
-  POST /workflowlevel2: Create WorkflowLevel2
	-  Add the property `workflowleve2_uuid` to the data model and set the value to the UUID from the response.
	-  If it's got a parent WorkflowLevel2, then add the property `parent_workflowlevel2` to the data model and set the value to the UUID of its parent WorkflowLevel2.

Appendix: Reserved endpoint names
---------------------------------

The following endpoint names are reserved by Buildly and may not be implemented in your services' APIs:

- `/admin`
- `/oauth`
- `/health_check`
- `/docs`
- `/complete`
- `/disconnect`
- `/static`
- `/workflow`
- `/core`
- `/logicmodule`
- `/milestone`
- `/organization`
