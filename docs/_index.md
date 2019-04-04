+++
title = "BiFrost"
api_url = "walhall/bifrost"
+++

# BiFrost

## Summary

BiFrost is the core service of every Walhall app. It exposes all of the app's microservices as a single API and acts as the main authentication layer. It also provides the basic data model of the app and handles user management and permissions.

When you create a Walhall app and choose [logic modules](/marketplace#what-are-logic-modules) or [blueprints](/marketplace#make-your-own-logic-module), they are pre-configured to communicate with BiFrost. So is the app's frontend, [Midgard](/walhall/midgard).

## Data model

All [logic modules](/marketplace#what-are-logic-modules) incorporate the BiFrost data model. These are the most important models:

-  **Organization:** The top-level class of a Walhall app.
-  **CoreUser:** A registered user of a Walhall app who belongs to an Organization.
-  **CoreGroup:** A model that defines a group of CoreUsers with specific permissions in the context of a given WorkflowLevel (1 or 2).
-  **WorkflowLevel:** WorkflowLevels are core objects that define the data hierarchy of the app. They are associated with each data model in each backend service. There are two types of WorkflowLevels: **WorkflowLevel1** and **WorkflowLevel2.** See the [permissions section](#permissions-model) for more details.

You can manage these data models in your app by making requests to the [BiFrost API](/api/walhall/bifrost).

## Permissions model

The BiFrost permissions model follows the [role-based access control (RBAC) pattern](https://en.wikipedia.org/wiki/Role-based_access_control).

In Walhall, CoreUser permissions are assigned on the basis of which **CoreGroups** they belong to. Each CoreGroup is associated with one WorkflowLevel1 or one WorkflowLevel2. "Permissions" are defined as the ability to execute [CRUD operations](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) on the data model with which the WorkflowLevel is associated.

WorkflowLevel1s are top-level; all WorkflowLevel2s must be associated with a WorkflowLevel1 as a child object. However, WorkflowLevel2s can also be children of other WorkflowLevel2s -- a recursive permissions structure.

If a CoreGroup is given permissions to a WorkflowLevel1, then those permissions will cascade down to all child WorkflowLevel2s.

If a CoreGroup is given permissions to a WorkflowLevel2, then those permissions will cascade down to all child WorkflowLevel2s, but they will **not** have permissions to the WorkflowLevel1.

## API gateway

When your Walhall app is deployed, BiFrost runs a discovery process to determine which services are used in the app. As the API gateway, BiFrost receives API requests, enforces throttling and security policies, passes requests to the backend services, and then passes the response back to the requester.

In order to be discovered by BiFrost, your service must follow the [OpenAPI (Swagger) specification](https://swagger.io/specification/) and expose a **swagger.json file** on the `/docs` endpoint.

### SwaggerUI for your app

As part of the discovery process, BiFrost will combine the Swagger files from all the services and serve the combined API documentation at the `/docs` endpoint of the app via [SwaggerUI](https://swagger.io/tools/swagger-ui/). 

