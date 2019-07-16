+++
title = "Connect your service to BiFrost"
+++

# Connect your service to BiFrost

## Overview

This tutorial will explain how to connect an existing backend service to [BiFrost](/bifrost). 

Once you connect your service to BiFrost, it will be able to communicate with all of your other services over a core authentication layer. All of its endpoints will be exposed as part of a single API that BiFrost puts together from all of the services. You also have the option to use BiFrost for managing permissions and users.

## Requirements

There are no requirements for the language or framework used to code your service. It must only satisfy these conditions in order to connect to BiFrost:

1.  Your service must include a **Dockerfile.**
2.  Your service must follow the [OpenAPI (Swagger) spec](https://swagger.io/docs/specification/about/) and expose a `swagger.json` file at the `/docs` endpoint.
3.  Your service must implement the [Walhall CI/CD pipeline](/walhall#walhall-s-ci-cd-pipeline).
4.  Your service must use an [OAuth2](https://oauth.net/2/) library with support for [JSON Web Tokens (JWTs)](https://jwt.io). See the [JWT authorization](#implement-jwt-authorization) section for more information.
5.  At this time, your service must run on port `8080`; in the future, you will be able to specify the container port in Walhall.

## Implement JWT authorization

Next, you need to implement BiFrost's authorization method. 

### About BiFrost authorization

For external requests to logic modules (e.g., [Midgard](/midgard) users), BiFrost uses an [OAuth2](https://oauth.net/2/) flow to issue [JSON Web Tokens (JWTs)](https://jwt.io) signed with RS256. 

Inside the container where the service is deployed, Walhall exposes BiFrost's **public key** as the environment variable `JWT_PUBLIC_KEY_RSA_BIFROST`. The service must use this environment variable to decode requests from BiFrost. 

BiFrost passes the JWT to the service in the `Authorization` HTTP header using the format `JWT {token}`. Example:

```
Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJiaWZyb3N0IiwiZXhwIjoxNTYwNjA0OTc2LCJpYXQiOjE1NjA1MTg1NzYsImNvcmVfdXNlcl91dWlkIjoiODJiZGI2YTMtMjExOS00MThmLThjMmQtY2FhYjdlYmI4OTc1Iiwib3JnYW5pemF0aW9uX3V1aWQiOiJiMjY1YmFkNS1iODEyLTRmNDItYjNlZS0zNDFlYmJiNzJjNmIiLCJzY29wZSI6InJlYWQgd3JpdGUiLCJ1c2VybmFtZSI6ImFkbWluIn0.CV8PafWuGDZSpWRI5wC6btO6cyt9udI9P5uLBdnHzVhbbIY-LH1o3qBgnRf0OAreUhRfl7zBTBMNO56pbyWeyg
```

### Example using PyJwt

Here's an example using the [PyJwt library](https://pyjwt.readthedocs.io/en/latest/). It takes the `encoded_jwt` from the HTTP header and decodes it with the `JWT_PUBLIC_KEY_RSA_BIFROST` environment variable:

```python
import jwt

jwt.decode(encoded_jwt, os.environ['JWT_PUBLIC_KEY_RSA_BIFROST'], algorithms=['RS256'])
```

The BiFrost JWT payload looks like this:

```json
{
	"core_user_uuid": "fd76ce0c-d8be-4aa6-91ed-59e698f6af60",
	"exp": 1560472728,
	"iat": 1560436728,
	"iss": "bifrost",
	"organization_uuid": "70f0d039-e3d9-427e-b161-4e95dbd9e918",
	"scope": "read write",
	"username": "admin"
}
```

-  `core_user_uuid`: UUID of the [CoreUser](/bifrost#coreuser) who initiated the request.
-  `exp`: Datetime when the token expires.
-  `iat`: Datetime when the token was issued.
-  `iss`: Issuer of the JWT. This will always be `bifrost`.
-  `organization_uuid`: UUID of the [Organization](/bifrost#organization) that contains the CoreUser who initiated the request.
-  `scope`: Permission scopes granted in the request by BiFrost.
-  `username`: The [Midgard username](/midgard) of the CoreUser who initiated the request.


## Add service to your Walhall app and deploy

Now you have completed the minimum necessary configurations to make your service work with BiFrost. The last step is to add it to a Walhall app as a [logic module](/library#about-logic-modules) and deploy it.

See the [Add custom logic module tutorial](/walhall/tutorials/add-logic-module-to-application) for instructions on how to do so.

## (Optional) Implement BiFrost permissions model

If you want to implement the [BiFrost permissions model](/bifrost#permissions-model) in your services, then you need to create **WorkflowLevels** for each of your data models and implement them in the models. We recommend creating WorkflowLevel1s for all top-level data models in your service and WorkflowLevel2s for defining any nested data relationships.

See the [BiFrost documentation](/bifrost#example-implementation) for an example of how to implement WorkflowLevels in your data model.

You must [create and deploy a Walhall app](/walhall/tutorials/get-started) before you can implement the BiFrost permissions model.

Once you've done so, use the following endpoints of your **app's API URL** to define WorkflowLevels:

-  [POST /workflowlevel1](/api/bifrost#!/workflowlevel1/workflowlevel1_create): Create WorkflowLevel1
	-  Add the property `workflowleve1_uuid` to the data model and set the value to the UUID from the response.
-  [POST /workflowlevel2](/api/bifrost#!/workflowlevel2/workflowlevel2_create): Create WorkflowLevel2
	-  Add the property `workflowleve2_uuid` to the data model and set the value to the UUID from the response.
	-  If it's got a parent WorkflowLevel2, then add the property `parent_workflowlevel2` to the data model and set the value to the UUID of its parent WorkflowLevel2.

You can find your **API URL** next to BiFrost in your app's overview page.

![Screenshot: BiFrost API URL](/walhall/_assets/bifrost-api-url.png)

## Appendix: Reserved endpoint names

The following endpoint names are reserved by BiFrost and may not be implemented in your services' APIs:

- `/admin`
- `/oauth`
- `/health_check`
- `/docs`
- `/complete`
- `/disconnect`
- `/static`
- `/graphql`
- `/workflow`
- `/core`
- `/logicmodule`
- `/user`
- `/group`
- `/milestone`
- `/organization`
