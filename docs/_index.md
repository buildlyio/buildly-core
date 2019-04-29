+++
title = "BiFrost"
api_url = "walhall/bifrost"
+++

# BiFrost

## Overview

BiFrost is the core service of every Walhall application. It exposes all of the application's microservices as a single API and acts as the main authentication layer. It also provides the basic data model of the application and handles user management and permissions.

When you create a Walhall application and choose [logic modules](/marketplace#what-are-logic-modules) or [blueprints](/marketplace#make-your-own-logic-module), they are pre-configured to communicate with BiFrost. So is the application's frontend, [Midgard](/walhall/midgard).

## Data model

All of the data models exposed by BiFrost are managed over the [BiFrost API](/api/walhall/bifrost).

### Organization

The Organization is the top-level class of every Walhall application. Everything contained within an organization---users, groups, and WorkflowLevels---can only be accessed by entities within the organization, with the exception of global CoreGroups (see below).

### CoreUser

A CoreUser is a registered user of a Walhall application. Every CoreUser must belong to a **CoreGroup.**

### CoreGroup

A CoreGroup defines a group of CoreUsers with specific permissions in the context of a given WorkflowLevel (1 or 2).

### WorkflowLevels

WorkflowLevels are core objects that define the data hierarchy of the application. Every data model exposed by a logic module uses a WorkflowLevel. There are two types of WorkflowLevels: **WorkflowLevel1** and **WorkflowLevel2.** See the [permissions section](#permissions-model) for more details.

## Permissions model

The BiFrost permissions model follows the [role-based access control (RBAC) pattern](https://en.wikipedia.org/wiki/Role-based_access_control).

In Walhall, permissions are granted to CoreUsers by their **CoreGroups.** Each CoreGroup can be associated with one or more WorkflowLevels. "Permissions" are defined as the ability to execute [CRUD operations](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) on WorkflowLevels.

WorkflowLevel1s are top-level data model associations. All WorkflowLevel2s are child objects of a WorkflowLevel1. However, WorkflowLevel2s can also be children of other WorkflowLevel2s as part of a recursive permissions structure. If a CoreGroup is given permissions to a WorkflowLevel, then those permissions will cascade down to all child WorkflowLevels.

By default, all CoreGroups can only have permissions defined to entities within their Organization. You can define a **global CoreGroup** that has permissions to all organizations by setting the `is_global` property to `true`.

## API gateway

When your Walhall application is deployed, BiFrost runs a discovery process to determine which services are used in the application. As the API gateway, BiFrost receives API requests, enforces throttling and security policies, passes requests to the backend services, and then passes the response back to the requester.

In order to be discovered by BiFrost, your service must follow the [OpenAPI (Swagger) specification](https://swagger.io/specification/) and expose a **swagger.json file** on the `/docs` endpoint.

### SwaggerUI for your application

As part of the discovery process, BiFrost will combine the Swagger files from all the services and serve the combined API documentation at the `/docs` endpoint of the application via [SwaggerUI](https://swagger.io/tools/swagger-ui/). 

