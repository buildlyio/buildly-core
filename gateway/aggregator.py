import json
import logging
import hashlib

from core.models import LogicModule
from .models import SwaggerVersionHistory
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
        Check for changes in the API and update the LogicModule entry
        with the new spec and version. If the version has changed,
        log the change in a separate model.

        :return: a dict of swagger spec
        """
        swagger_apis = {}
        if 'apis' in self.configuration:  # Check if apis is in the config file
            for endpoint_name, schema_url in self.configuration['apis'].items():
                if endpoint_name not in swagger_apis:
                    try:
                        # Fetch stored specification and version
                        logic_module = LogicModule.objects.filter(endpoint_name=endpoint_name).first()
                        stored_spec = logic_module.api_specification if logic_module else None
                        stored_version = logic_module.swagger_version if logic_module else None
                        stored_hash = self._get_hash(stored_spec) if stored_spec else None

                        # Fetch the latest specification from the remote API
                        response = utils.get_swagger_from_url(schema_url)
                        latest_spec = response.json()
                        latest_version = latest_spec.get('info', {}).get('version', 'unknown')
                        latest_hash = self._get_hash(latest_spec)

                        # Log the version change in a separate model
                        if stored_version != latest_version:
                            SwaggerVersionHistory.objects.create(
                                endpoint_name=endpoint_name,
                                old_version=stored_version,
                                new_version=latest_version,
                            )

                        # Check for changes in the version or specification
                        if stored_version != latest_version or stored_hash != latest_hash:
                            # Update the LogicModule entry with the new spec and version
                            LogicModule.objects.update_or_create(
                                endpoint_name=endpoint_name,
                                defaults={
                                    'api_specification': latest_spec,
                                    'swagger_version': latest_version,
                                },
                            )

                        swagger_apis[endpoint_name] = {
                            'spec': latest_spec,
                            'url': schema_url,
                        }
                    except ConnectionError as error:
                        logger.warning(f"Connection error for {schema_url}: {error}")
                    except TimeoutError as error:
                        logger.warning(f"Timeout error for {schema_url}: {error}")
                    except ValueError as error:
                        logger.warning(f"Invalid response from {schema_url}: {error}")
        return swagger_apis

    def _get_hash(self, data: dict) -> str:
        """
        Generate a hash for the given data.

        :param data: The data to hash.
        :return: A SHA-256 hash of the data.
        """
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def _update_specification(self, name: str, api_name: str, api_spec: dict) -> dict:
        """
        Update names of the specification of a service's API.

        :param name: The name of the specification to update.
        :param api_name: The name of the service.
        :param api_spec: The specification of the service's API.
        :return: A dict with the updated specification.
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
        Merge aggregates.

        :return: Aggregate of all APIs.
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

            # Update the definitions
            if 'definitions' in api_spec['spec']:
                basic_swagger['definitions'].update(
                    self._update_specification('definitions', api, api_spec)
                )

            # Update the paths to match with the gateway
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
        Replace the current operation ID to avoid collision.

        :param swagger: A dict with the API specification in the Swagger format.
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
        Generate a Swagger document from all the APIs' Swagger documents.

        :return: A dict with all the APIs' Swagger documents aggregated.
        """
        merged_apis = self.merge_aggregates()
        self.generate_operation_id(merged_apis)

        return merged_apis