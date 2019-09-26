.. _proxy:

# Proxy pattern

![Diagram: Proxy pattern using Buildly](../_static/images/proxy-pattern.png)

You can use Buildly's **API gateway** to implement a proxy pattern in your microservice architecture. Add all your services to Buildly via the API and it will run an auto-discovery process to identify all of the endpoints and combine them into a single API. All requests to and from the logic modules will be routed through Buildly. Authentication is handled with a [JSON Web Token (JWT)](https://jwt.io).

All you need to do to use the API gateway with your logic modules is to ensure that they expose a [Swagger file](https://swagger.io/docs/specification/about/) (`swagger.json`) at the `/docs` endpoint.
