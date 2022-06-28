import json
import logging

from core.models import LogicModule
from gateway import utils

logger = logging.getLogger(__name__)


class SwaggerAggregator(object):
    """
    Create an API from an aggregation of APIs
    """

    def __init__(self, configuration: dict):
        self.configuration = configuration

    def get_aggregate_swagger(self) -> dict:
        """
        Get swagger files associated with the aggregates.

        :return: a dict of swagger spec
        """
        swagger_apis = {}
        if 'apis' in self.configuration:  # Check if apis is in the config file
            for endpoint_name, schema_url in self.configuration['apis'].items():
                if endpoint_name not in swagger_apis:
                    # Get the swagger.json
                    try:
                        # Use stored specification of the module
                        spec_dict = (
                            LogicModule.objects.values_list(
                                'api_specification', flat=True
                            )
                            .filter(endpoint_name=endpoint_name)
                            .first()
                        )

                        # Pull specification of the module from its service and store it
                        if spec_dict is None:
                            response = utils.get_swagger_from_url(schema_url)
                            spec_dict = response.json()
                            LogicModule.objects.filter(
                                endpoint_name=endpoint_name
                            ).update(api_specification=spec_dict)

                        swagger_apis[endpoint_name] = {
                            'spec': spec_dict,
                            'url': schema_url,
                        }
                    except ConnectionError as error:
                        logger.warning(error)
                    except TimeoutError as error:
                        logger.warning(error)
                    except ValueError:
                        logger.info('Cannot remove {} from errors'.format(schema_url))
        return swagger_apis

    def _update_specification(self, name: str, api_name: str, api_spec: dict) -> dict:
        """
        Update names of the specification of a service's API

        :param name: of the specification that should be updated
        :param api_name: name of the service
        :param api_spec: specification of the service's API
        :return: a dict with the updated specification
        """
        result = {}
        if name in api_spec['spec']:
            specification = api_spec['spec'][name]
            for spec_name, spec_def in specification.items():
                spec_name = '{}{}'.format(api_name, spec_name)
                result[spec_name] = spec_def

        return result

    def merge_aggregates(self) -> dict:
        """
        Merge aggregates

        :return: aggregate of all apis
        """
        basic_swagger = {
            'swagger': '2.0',
            'info': self.configuration.get('info'),
            'host': self.configuration.get('host', None),
            'basePath': self.configuration.get('basePath', None),
            'consumes': self.configuration.get('consumes', None),
            'produces': self.configuration.get('produces', None),
            'definitions': {},
            'paths': {},
        }

        swagger_apis = self.get_aggregate_swagger()
        for api, api_spec in swagger_apis.items():
            # Rename definition to avoid collision.
            api_spec['spec'] = json.loads(
                json.dumps(api_spec['spec']).replace(
                    '#/definitions/', u'#/definitions/{}'.format(api)
                )
            )

            # update the definitions
            if 'definitions' in api_spec['spec']:
                basic_swagger['definitions'].update(
                    self._update_specification('definitions', api, api_spec)
                )

            # update the paths to match with the gateway
            if 'paths' in api_spec['spec']:
                if api == 'buildly':
                    basic_swagger['paths'].update(api_spec['spec']['paths'])
                else:
                    api_name = '/{}'.format(api)
                    basic_swagger['paths'].update(
                        self._update_specification('paths', api_name, api_spec)
                    )

        return basic_swagger

    def generate_operation_id(self, swagger):
        """
        Replace the current operation id to uuid to avoid collision

        :param swagger: a dict with the API specification in the swagger format
        """

        for path, path_spec in swagger['paths'].items():
            service_name = path.split('/')[1]
            for action, action_spec in path_spec.items():
                if 'operationId' in action_spec:
                    current_op_id = action_spec['operationId']
                    action_spec['operationId'] = '{}.{}'.format(
                        service_name, current_op_id
                    )

    def generate_swagger(self):
        """
        Generate a swagger from all the apis swagger

        :return: a dict with all the apis swagger aggregated
        """
        merged_apis = self.merge_aggregates()
        self.generate_operation_id(merged_apis)

        return merged_apis
