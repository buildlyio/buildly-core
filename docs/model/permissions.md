# Permissions model

The Buildly permissions model follows the RBAC pattern.

Permissions are granted to CoreUsers by their **CoreGroups.** Each CoreGroup can be associated with one or more WorkflowLevels. "Permissions" are defined as the ability to execute [CRUD operations](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) on WorkflowLevels.

If a CoreGroup is given permissions to a WorkflowLevel, then those permissions will cascade down to all child WorkflowLevels.

By default, all CoreGroups can only have permissions defined to entities within their Organization. You can define a **global CoreGroup** that has permissions to all organizations by setting the `is_global` property to `true`.

## Organization

The Organization is the top-level class of the Buildly permissions model. Everything contained within an organization---users, groups, and WorkflowLevels---can only be accessed by entities within the organization, with the exception of global CoreGroups (see below).

## CoreUser

A CoreUser is a registered user of an application. Every CoreUser must belong to a **CoreGroup.**

## CoreGroup

A CoreGroup defines a group of CoreUsers with specific permissions in the context of a given WorkflowLevel (1 or 2).

## WorkflowLevels

Buildly allows you to define nested data hierarchies in your microservice architecture by using **WorkflowLevels.** There are two types of WorkflowLevels: **WorkflowLevel1** and **WorkflowLevel2.** WorkflowLevel2s can be nested within other WorkflowLevel2s as child objects, but they must always be associated with a parent WorkflowLevel1.

By creating WorkflowLevels for each model in your microservice architecture, you can enable them to share data by implementing their WorkflowLevel UUIDs as foreign keys. 

You can define WorkflowLevels using the Buildly API once you have deployed your application.

### Example implementation

Suppose you want to create a microservice application for managing factories that employ a variety of robots to manufacture a variety of products.

-  The **Factory** is the top of the data hierarchy, so the Factory model would be considered the WorkflowLevel1. 
-  Each factory employs a set of **robots,** so the Robot model would be considered a WorkflowLevel2 associated with the "Factory" WorkflowLevel1. 
-  Each robot manufactures a set of **products,** so the Product model would be considered a WorkflowLevel2 with the Robot model as its parent.

Follow these steps to implement this data hierarchy in Buildly:

1.  Create a **WorkflowLevel1** with the name "Factory" using your app's `POST /workflowlevel1` endpoint.
2.  Add the `workflowlevel1_uuid` property to your Factory data model and set the value to the UUID of the Factory WorkflowLevel1 you just created.
3.  Create a **WorkflowLevel2** with the name "Robot" using your app's `POST /workflowlevel2` endpoint. Set the value of `workflowlevel1` to the UUID of the Factory WorkflowLevel1.
4.  Add the following properties to your Robot data model:
    -  `workflowlevel1_uuid`: UUID of the Factory WorkflowLevel1.
    -  `workflowlevel2_uuid`: UUID of the Robot WorkflowLevel2.
5.  Create a **WorkflowLevel2** with the name "Product" using your app's `POST /workflowlevel2` endpoint. Set the value of `workflowlevel1` to the UUID of your Factory WorkflowLevel1, and set the value of `parent_workflowlevel2` to the UUID of your Robot WorkflowLevel2.
6.  Add the following properties to your Product data model:
    -  `workflowlevel1_uuid`: UUID of the Factory WorkflowLevel1.
    -  `workflowlevel2_uuid`: UUID of the Robot WorkflowLevel2.

Associating your data models with WorkflowLevels enables them to be reused and dynamically swapped out. For example, if some of your factories employ humans to build the same products, you could create a **Human** WorkflowLevel2 and add the Human WorkflowLevel2 UUID as another parent to the Product data model.
 