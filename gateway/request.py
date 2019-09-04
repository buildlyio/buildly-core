import logging
import json
import uuid
import asyncio
from urllib.error import URLError
from typing import Any, Dict, Union

import requests
import aiohttp
from bravado_core.spec import Spec
from django.http.request import QueryDict
from django.forms.models import model_to_dict
from rest_framework.request import Request

from . import exceptions
from . import utils
from .models import LogicModule
from .clients import SwaggerClient, AsyncSwaggerClient
from datamesh.services import DataMesh
from workflow import models as wfm

logger = logging.getLogger(__name__)


class GatewayResponse(object):
    """
    Response object used with GatewayRequest
    """

    def __init__(self, content: Any, status_code: int, headers: Dict[str, str]):
        self.content = content
        self.status_code = status_code
        self.headers = headers


class BaseGatewayRequest(object):
    """
    Base class for implementing gateway logic for redirecting incoming request to underlying micro-services.
    First it retrieves a Swagger specification of the micro-service
    to validate incoming request's operation against it.
    """

    SWAGGER_CONFIG = {
        'validate_requests': False,
        'validate_responses': False,
        'use_models': False,
        'validate_swagger_spec': False,
    }

    def __init__(self, request: Request, **kwargs):
        self.request = request
        self.url_kwargs = kwargs
        self._logic_modules = dict()
        self._specs = dict()
        self._data = dict()

    def perform(self):
        raise NotImplementedError('You need to implement this method')

    def _get_logic_module(self, service_name: str) -> LogicModule:
        """ Retrieve LogicModule by service name. """
        if service_name not in self._logic_modules:
            try:
                self._logic_modules[service_name] = LogicModule.objects.get(endpoint_name=service_name)
            except LogicModule.DoesNotExist:
                raise exceptions.ServiceDoesNotExist(f'Service "{service_name}" not found.')
        return self._logic_modules[service_name]

    def get_datamesh(self) -> DataMesh:
        """ Get DataMesh object for the top level model """
        service_name = self.url_kwargs['service']
        logic_module = self._get_logic_module(service_name)

        # find out forwards relations through logic module from request as origin
        padding = self.request.path.index(f'/{logic_module.endpoint_name}')
        endpoint = self.request.path[len(f'/{logic_module.endpoint_name}')+padding:]
        endpoint = endpoint[:endpoint.index('/', 1) + 1]
        return DataMesh(logic_module_endpoint=logic_module.endpoint_name,
                        model_endpoint=endpoint,
                        access_validator=utils.ObjectAccessValidator(self.request))


class GatewayRequest(BaseGatewayRequest):
    """
    Allows to perform synchronous requests to underlying services with requests package
    """

    def perform(self) -> GatewayResponse:
        """
        Make request to underlying service(s) and returns aggregated response.
        """
        # init swagger spec from the service swagger doc file
        try:
            spec = self._get_swagger_spec(self.url_kwargs['service'])
        except exceptions.ServiceDoesNotExist as e:
            return GatewayResponse(e.content, e.status, {'Content-Type': e.content_type})

        # create a client for performing data requests
        client = SwaggerClient(spec, self.request)

        # perform a service data request
        content, status_code, headers = client.request(**self.url_kwargs)

        # aggregate/join with the JoinRecord-models
        if 'join' in self.request.query_params and status_code == 200 and type(content) in [dict, list]:
            try:
                self._join_response_data(resp_data=content)
            except exceptions.ServiceDoesNotExist as e:
                logger.error(e.content)

        # old DataMesh aggregation TODO: remove after migrating to the new one
        if self.request.query_params.get('aggregate', '_none').lower() == 'true' and status_code == 200:
            try:
                self._aggregate_response_data(resp_data=content)
            except exceptions.ServiceDoesNotExist as e:
                logger.error(e.content)

        if type(content) in [dict, list]:
            content = json.dumps(content, cls=utils.GatewayJSONEncoder)

        return GatewayResponse(content, status_code, headers)

    def _get_swagger_spec(self, endpoint_name: str) -> Spec:
        """Get Swagger spec of specified service."""
        logic_module = self._get_logic_module(endpoint_name)
        schema_url = utils.get_swagger_url_by_logic_module(logic_module)

        if schema_url not in self._specs:
            try:
                response = requests.get(schema_url)
                spec_dict = response.json()
            except URLError:
                raise URLError(f'Make sure that {schema_url} is accessible.')

            swagger_spec = Spec.from_dict(spec_dict, config=self.SWAGGER_CONFIG)
            self._specs[schema_url] = swagger_spec

        return self._specs[schema_url]

    def _join_response_data(self, resp_data: Union[dict, list]) -> None:
        """
        Aggregates data from the requested service and from related services.
        Uses DataMesh relationship model for this.
        """
        self.request._request.GET = QueryDict(mutable=True)

        if isinstance(resp_data, dict):
            if 'results' in resp_data:
                # In case of pagination take 'results' as a items data
                resp_data = resp_data.get('results', None)

        datamesh = self.get_datamesh()
        client_map = {}
        for service in datamesh.related_logic_modules:
            spec = self._get_swagger_spec(service)
            client_map[service] = SwaggerClient(spec, self.request)
        datamesh.extend_data(resp_data, client_map)

    # ===================================================================
    # OLD DATAMESH METHODS (TODO: remove after migrating to new DataMesh)
    def _aggregate_response_data(self, resp_data: Union[dict, list]):
        """
        Aggregate data from first response
        """
        service_name = self.url_kwargs['service']

        if isinstance(resp_data, dict):
            if 'results' in resp_data:
                # DRF API payload structure
                resp_data = resp_data.get('results', None)

        logic_module = self._get_logic_module(service_name)

        if isinstance(resp_data, list):
            for data in resp_data:
                extension_map = self._generate_extension_map(
                    logic_module=logic_module,
                    model_name=self.url_kwargs['model'],
                    data=data
                )
                r = self._expand_data(extension_map)
                data.update(**r)
        elif isinstance(resp_data, dict):
            extension_map = self._generate_extension_map(
                logic_module=logic_module,
                model_name=self.url_kwargs['model'],
                data=resp_data
            )
            r = self._expand_data(extension_map)
            resp_data.update(**r)

    def _expand_data(self, extend_models: list):
        """
        Use extension maps to fetch data from different services and
        replace the relationship key by real data.
        """
        result = dict()
        for extend_model in extend_models:
            content = None
            if extend_model['service'] == 'buildly':
                if hasattr(wfm, extend_model['model']):
                    cls = getattr(wfm, extend_model['model'])
                    uuid_name = self._get_buildly_uuid_name(cls)
                    lookup = {
                        uuid_name: extend_model['pk']
                    }
                    try:
                        obj = cls.objects.get(**lookup)
                    except cls.DoesNotExist as e:
                        logger.info(e)
                    except ValueError:
                        logger.info(f' Not found: {extend_model["model"]} with uuid_name={extend_model["pk"]}')
                    else:
                        utils.validate_object_access(self.request, obj)
                        content = model_to_dict(obj)
            else:
                spec = self._get_swagger_spec(extend_model['service'])

                # remove query_params from original request
                self.request._request.GET = QueryDict(mutable=True)

                # create a client for performing data requests
                client = SwaggerClient(spec, self.request)

                # perform a service data request
                content, _, _ = client.request(**extend_model)

            if content is not None:
                result[extend_model['relationship_key']] = content

        return result

    def _generate_extension_map(self, logic_module: LogicModule, model_name: str, data: dict):
        """
        Generate a list of relationship map of a specific service model.
        """
        extension_map = []
        if not logic_module.relationships:
            logger.warning(f'Tried to aggregate but no relationship defined in {logic_module}.')
            return extension_map
        for k, v in logic_module.relationships[model_name].items():
            value = v.split('.')
            collection_args = {
                'service': value[0],
                'model': value[1],
                'pk': str(data[k]),
                'relationship_key': k
            }
            extension_map.append(collection_args)

        return extension_map

    def _get_buildly_uuid_name(self, model):
        for field in model._meta.fields:
            if field.name.endswith('uuid') and field.unique and \
                    field.default == uuid.uuid4:
                return field.name
    # ==================================================================


class AsyncGatewayRequest(BaseGatewayRequest):
    """
    Allows to perform asynchronous requests to underlying services with asyncio and aiohttp package
    """

    def perform(self) -> GatewayResponse:
        """
        Override base class's method for asynchronous execution. Wraps async method.
        """
        result = {}
        asyncio.run(self.async_perform(result))
        if 'response' not in result:
            raise exceptions.GatewayError('Error performing asynchronous gateway request')
        return result['response']

    async def async_perform(self, result: dict):
        try:
            spec = await self._get_swagger_spec(self.url_kwargs['service'])
        except exceptions.ServiceDoesNotExist as e:
            return GatewayResponse(e.content, e.status, {'Content-Type': e.content_type})

        # create a client for performing data requests
        client = AsyncSwaggerClient(spec, self.request)

        # perform a service data request
        content, status_code, headers = await client.request(**self.url_kwargs)

        # aggregate/join with the JoinRecord-models
        if 'join' in self.request.query_params and status_code == 200 and type(content) in [dict, list]:
            try:
                await self._join_response_data(resp_data=content)
            except exceptions.ServiceDoesNotExist as e:
                logger.error(e.content)

        if type(content) in [dict, list]:
            content = json.dumps(content, cls=utils.GatewayJSONEncoder)

        result['response'] = GatewayResponse(content, status_code, headers)

    async def _get_swagger_spec(self, endpoint_name: str) -> Spec:
        """ Gets swagger spec asynchronously and adds it to specs cache """
        logic_module = self._get_logic_module(endpoint_name)
        schema_url = utils.get_swagger_url_by_logic_module(logic_module)

        if schema_url not in self._specs:
            async with aiohttp.ClientSession() as session:
                async with session.get(schema_url) as response:
                    try:
                        spec_dict = await response.json()
                    except aiohttp.ContentTypeError:
                        raise exceptions.GatewayError(
                            f'Failed to parse swagger schema from {schema_url}. Should be JSON.'
                        )
                swagger_spec = Spec.from_dict(spec_dict, config=self.SWAGGER_CONFIG)
                self._specs[schema_url] = swagger_spec
        return self._specs[schema_url]

    async def _join_response_data(self, resp_data: Union[dict, list]) -> None:
        """
        Aggregates data from the requested service and from related services asynchronously.
        Uses DataMesh relationship model for this.
        """
        self.request._request.GET = QueryDict(mutable=True)

        if isinstance(resp_data, dict):
            if 'results' in resp_data:
                # In case of pagination take 'results' as a items data
                resp_data = resp_data.get('results', None)

        datamesh = self.get_datamesh()
        tasks = []
        for service in datamesh.related_logic_modules:
            tasks.append(self._get_swagger_spec(service))
        specs = await asyncio.gather(*tasks)
        clients = map(lambda x: AsyncSwaggerClient(x, self.request), specs)
        client_map = dict(zip(datamesh.related_logic_modules, clients))
        await datamesh.async_extend_data(resp_data, client_map)
