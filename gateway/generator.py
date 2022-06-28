from drf_yasg import generators as drf_gen
from drf_yasg import openapi

from gateway import utils
from gateway.aggregator import SwaggerAggregator


class OpenAPISchemaGenerator(drf_gen.OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema_urls = utils.get_swagger_urls()
        config_aggregator = {
            'info': {'title': 'API Gateway', 'description': '', 'version': '1.0'},
            'apis': schema_urls,
            'produces': [
                'application/json',
                'application/x-www-form-urlencoded',
                'multipart/form-data',
            ],
            'consumes': [
                'application/json',
                'application/x-www-form-urlencoded',
                'multipart/form-data',
            ],
        }
        sw_aggregator = SwaggerAggregator(config_aggregator)
        swagger_spec = sw_aggregator.generate_swagger()

        endpoints = self.get_endpoints(request)
        components = openapi.ReferenceResolver(openapi.SCHEMA_DEFINITIONS)
        paths, prefix = self.get_paths(endpoints, components, request, public)
        paths.update(swagger_spec['paths'])
        components['definitions'].update(swagger_spec['definitions'])

        url = self.url
        if url is None and request is not None:
            url = request.build_absolute_uri()

        return openapi.Swagger(
            info=self.info,
            paths=paths,
            consumes=swagger_spec['consumes'],
            produces=swagger_spec['produces'],
            security_definitions=swagger_spec.get('security_definitions', None),
            security=swagger_spec.get('security', None),
            _url=url,
            _version=self.version,
            _prefix=prefix,
            **dict(components)
        )
