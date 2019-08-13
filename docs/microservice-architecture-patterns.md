# Microservice architecture patterns with BiFrost

BiFrost makes it possible to implement a variety of common microservice architecture patterns.

![Diagram: Humanitec flex pattern for a microservice architecture using BiFrost](_assets/flex-pattern.png)

## Proxy pattern

![Diagram: Proxy pattern using BiFrost](_assets/proxy-pattern.png)

You can use BiFrost's **API gateway** to implement a proxy pattern in your microservice architecture. When you create a Walhall app and add your logic modules, BiFrost will run an auto-discovery process to identify all of the endpoints and combine them into a single API. All requests to and from the logic modules will be routed through BiFrost. Authentication is handled with a [JSON Web Token (JWT)](https://jwt.io).

All you need to do to use the API gateway with your logic modules is to ensure that they expose a [Swagger file](https://swagger.io/docs/specification/about/) (`swagger.json`) at the `/docs` endpoint.

## Aggregator pattern

![Diagram: Aggregator pattern using BiFrost](_assets/aggregator-pattern.png)

BiFrost includes a **data mesh** that can be used to implement an aggregator pattern. The data mesh is a service in BiFrost running alongside the API gateway that contains a list of logic modules in the app and how they can be joined. It creates a lookup table of each of these connections. Then, the app frontend can query this table for each data type's unique ID, write the individual REST queries for each service, and then pull that service data back into one request object with a join of the data.

## Async pattern

![Diagram: Async pattern using BiFrost](_assets/async-pattern.png)

If you would prefer not to use the API gateway or data mesh, you can still use BiFrost in an async pattern. Every app environment in Walhall includes [RabbitMQ](https://www.rabbitmq.com/), and both BiFrost and Walhall include [Celery](http://www.celeryproject.org/). When you add a logic module to your app, Walhall will publish to your app's RabbitMQ feed. The message will be consumed by BiFrost's Celery, and BiFrost will add a new record to the database of logic modules in the app. 

