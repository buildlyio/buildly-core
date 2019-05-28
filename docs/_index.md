+++
title = "BiFrost"
api_url = "bifrost"
aliases = [
	"/walhall/bifrost"
]
+++

# BiFrost

## Overview

BiFrost is an API gateway and core authentication layer for microservice architectures. 

When you add BiFrost to your [Walhall application](/walhall), it registers every endpoint from the microservices through an auto-discovery process and combines them into a single API. BiFrost updates the API whenever a service is updated (i.e., a tag is pushed in GitHub).

BiFrost also provides a core data model for ensuring a consistent data hierarchy among your microservices, and it allows you to manage users and permissions using a [role-based access control (RBAC) model](https://en.wikipedia.org/wiki/Role-based_access_control).

You can choose whether or not to include BiFrost in your application during the creation process in the Walhall UI.

<!-- ## Tutorials

See the following tutorials for information on how to use BiFrost:

-  [Connect your services to BiFrost](/bifrost/tutorials/connect-services-to-bifrost) -->

## Data model

You can manage your application's data model by making calls to the [BiFrost API](/api/walhall/bifrost).

### Organization

The Organization is the top-level class of the BiFrost permissions model. Everything contained within an organization---users, groups, and WorkflowLevels---can only be accessed by entities within the organization, with the exception of global CoreGroups (see below).

### CoreUser

A CoreUser is a registered user of a Walhall application. Every CoreUser must belong to a **CoreGroup.**

### CoreGroup

A CoreGroup defines a group of CoreUsers with specific permissions in the context of a given WorkflowLevel (1 or 2).

### WorkflowLevels

WorkflowLevels are core objects that define the data hierarchy of the application. Every data model exposed by a logic module uses a WorkflowLevel. There are two types of WorkflowLevels: **WorkflowLevel1** and **WorkflowLevel2.** See the [permissions section](#permissions-model) for more details.

## Permissions model

The BiFrost permissions model follows the RBAC pattern.

Permissions are granted to CoreUsers by their **CoreGroups.** Each CoreGroup can be associated with one or more WorkflowLevels. "Permissions" are defined as the ability to execute [CRUD operations](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) on WorkflowLevels.

WorkflowLevel1s are top-level data model associations. All WorkflowLevel2s are child objects of a WorkflowLevel1. However, WorkflowLevel2s can also be children of other WorkflowLevel2s as part of a recursive permissions structure. If a CoreGroup is given permissions to a WorkflowLevel, then those permissions will cascade down to all child WorkflowLevels.

By default, all CoreGroups can only have permissions defined to entities within their Organization. You can define a **global CoreGroup** that has permissions to all organizations by setting the `is_global` property to `true`.

### SwaggerUI for your application

As part of the discovery process, BiFrost will combine the Swagger files from all the services and serve the combined API documentation at the `/docs` endpoint of the application via [SwaggerUI](https://swagger.io/tools/swagger-ui/). 
