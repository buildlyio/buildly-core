import logging
import json
import asyncio
from urllib.error import URLError
from typing import Any, Dict, Union

import aiohttp

from bravado_core.spec import Spec

from asgiref.sync import sync_to_async

from django.http.request import QueryDict
from rest_framework.request import Request

from datamesh.handle_request import RequestHandler
from datamesh.utils import delete_join_record
from gateway import exceptions
from gateway import utils
from core.models import LogicModule
from gateway.clients import SwaggerClient, AsyncSwaggerClient
from datamesh.services import DataMesh


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
                self._logic_modules[service_name] = LogicModule.objects.get(
                    endpoint_name=service_name
                )
            except LogicModule.DoesNotExist:
                raise exceptions.ServiceDoesNotExist(
                    f'Service "{service_name}" not found.'
                )
        return self._logic_modules[service_name]

    def get_datamesh(self) -> DataMesh:
        """ Get DataMesh object for the top level model """
        service_name = self.url_kwargs['service']
        logic_module = self._get_logic_module(service_name)

        # find out forwards relations through logic module from request as origin
        padding = self.request.path.index(f'/{logic_module.endpoint_name}')
        endpoint = self.request.path[len(f'/{logic_module.endpoint_name}') + padding:]
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
            return GatewayResponse(
                e.content, e.status, {'Content-Type': e.content_type}
            )

        # create a client for performing data requests
        client = SwaggerClient(spec, self.request)

        # perform a service data request
        content, status_code, headers = client.request(**self.url_kwargs)

        # calls to individual service as per relationship
        # call to join record insertion method
        # aggregate/join with the JoinRecord-models
        if ("join" or "extend") in self.request.query_params and status_code in [200, 201] and type(content) in [dict, list]:
            try:
                self._join_response_data(resp_data=content, query_params=self.request.query_params)
            except exceptions.ServiceDoesNotExist as e:
                logger.error(e.content)

        if 'join' in self.request.query_params and self.request.method == 'DELETE' and status_code == 204:
            delete_join_record(pk=self.url_kwargs['pk'], previous_pk=None)  # delete join record

        if type(content) in [dict, list]:
            content = json.dumps(content, cls=utils.GatewayJSONEncoder)

        return GatewayResponse(content, status_code, headers)

    def _get_swagger_spec(self, endpoint_name: str) -> Spec:
        """Get Swagger spec of specified service."""
        logic_module = self._get_logic_module(endpoint_name)
        schema_url = utils.get_swagger_url_by_logic_module(logic_module)

        if schema_url not in self._specs:
            try:
                # Use stored specification of the module
                spec_dict = logic_module.api_specification

                # Pull specification of the module from its service and store it
                if spec_dict is None:
                    response = utils.get_swagger_from_url(schema_url)
                    spec_dict = response.json()
                    logic_module.api_specification = spec_dict
                    logic_module.save()

            except URLError:
                raise URLError(f'Make sure that {schema_url} is accessible.')

            swagger_spec = Spec.from_dict(spec_dict, config=self.SWAGGER_CONFIG)
            self._specs[schema_url] = swagger_spec

        return self._specs[schema_url]

    def _join_response_data(self, resp_data: Union[dict, list], query_params: str) -> None:
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

        # check the request method
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            # fetch datamesh logic module info for current request from datamesh
            self.datamesh_relationship, self.request_param = datamesh.fetch_datamesh_relationship()
            self.request_method = self.request.method

            request_kwargs = {
                'query_params': query_params,
                'request_param': self.request_param,
                'datamesh_relationship': self.datamesh_relationship,
                'resp_data': resp_data,
                'request_method': self.request.method,
                'request': self.request
            }

            # handle datamesh requests
            request_handler = RequestHandler()
            response = request_handler.retrieve_relationship_data(request_kwargs=request_kwargs)

            # clear and update datamesh get response
            resp_data.clear()
            resp_data.update(response)

        else:

            for service in datamesh.related_logic_modules:
                spec = self._get_swagger_spec(service)
                client_map[service] = SwaggerClient(spec, self.request)

            datamesh.extend_data(resp_data, client_map)


class AsyncGatewayRequest(BaseGatewayRequest):
    """
    Async version of GatewayRequest that is safe to use in async contexts.
    All ORM/database calls are wrapped with sync_to_async.
    """

    async def perform(self) -> GatewayResponse:
        # Example: wrap any sync client or ORM calls with sync_to_async
        content, status_code, headers = await sync_to_async(self._client_request, thread_sensitive=False)()

        # Handle join/extend logic
        if ("join" in self.request.query_params or "extend" in self.request.query_params) and status_code in [200, 201] and type(content) in [dict, list]:
            try:
                await self._join_response_data(resp_data=content, query_params=self.request.query_params)
            except exceptions.ServiceDoesNotExist as e:
                logger.error(e.content)

        if 'join' in self.request.query_params and self.request.method == 'DELETE' and status_code == 204:
            await sync_to_async(delete_join_record)(pk=self.url_kwargs['pk'], previous_pk=None)

        if type(content) in [dict, list]:
            content = json.dumps(content, cls=utils.GatewayJSONEncoder)

        return GatewayResponse(content, status_code, headers)

    async def _client_request(self):
        # This wraps the sync client.request call
        return self.client.request(**self.url_kwargs)

    async def _get_swagger_spec(self, endpoint_name: str) -> Spec:
        """Get Swagger spec of specified service, async-safe."""
        logic_module = await self._get_logic_module(endpoint_name)
        schema_url = utils.get_swagger_url_by_logic_module(logic_module)

        if schema_url not in self._specs:
            try:
                # Use stored specification of the module
                spec_dict = logic_module.api_specification

                # Pull specification of the module from its service and store it
                if spec_dict is None:
                    response = await sync_to_async(utils.get_swagger_from_url)(schema_url)
                    spec_dict = response.json()
                    logic_module.api_specification = spec_dict
                    await sync_to_async(logic_module.save)()

            except URLError:
                raise URLError(f'Make sure that {schema_url} is accessible.')

            swagger_spec = Spec.from_dict(spec_dict, config=self.SWAGGER_CONFIG)
            self._specs[schema_url] = swagger_spec

        return self._specs[schema_url]

    async def _get_logic_module(self, service_name: str):
        if service_name not in self._logic_modules:
            try:
                self._logic_modules[service_name] = await sync_to_async(
                    LogicModule.objects.get
                )(endpoint_name=service_name)
            except LogicModule.DoesNotExist:
                raise exceptions.ServiceDoesNotExist(
                    f'Service \"{service_name}\" not found.'
                )
        return self._logic_modules[service_name]

    async def _join_response_data(self, resp_data: Union[dict, list], query_params: str) -> None:
        """
        Aggregates data from the requested service and from related services.
        Uses DataMesh relationship model for this.
        """
        self.request._request.GET = QueryDict(mutable=True)

        # Handle paginated results
        if isinstance(resp_data, dict) and 'results' in resp_data:
            resp_data = resp_data.get('results', None)

        # Get async DataMesh instance
        datamesh = await DataMesh.async_create(
            logic_module_endpoint=self.url_kwargs['service'],
            model_endpoint=self._extract_model_endpoint(),
            access_validator=utils.ObjectAccessValidator(self.request)
        )
        client_map = {}

        # POST/PUT/PATCH: handle relationship data via async RequestHandler
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            self.datamesh_relationship, self.request_param = await sync_to_async(datamesh.fetch_datamesh_relationship)()
            self.request_method = self.request.method

            request_kwargs = {
                'query_params': query_params,
                'request_param': self.request_param,
                'datamesh_relationship': self.datamesh_relationship,
                'resp_data': resp_data,
                'request_method': self.request.method,
                'request': self.request
            }

            # Async RequestHandler not implemented, so run in thread
            request_handler = RequestHandler()
            response = await sync_to_async(request_handler.retrieve_relationship_data, thread_sensitive=False)(request_kwargs=request_kwargs)

            # clear and update datamesh get response
            if hasattr(resp_data, 'clear') and hasattr(resp_data, 'update'):
                resp_data.clear()
                resp_data.update(response)
        else:
            # GET: build client_map and extend data async
            for service in datamesh.related_logic_modules:
                spec = await self._get_swagger_spec(service)
                client_map[service] = SwaggerClient(spec, self.request)

            await datamesh.async_extend_data(resp_data, client_map)

    def _extract_model_endpoint(self):
        """
        Helper to extract the model endpoint from the request path.
        """
        logic_module = self.url_kwargs['service']
        path = self.request.path
        padding = path.index(f'/{logic_module}')
        endpoint = path[len(f'/{logic_module}') + padding:]
        endpoint = endpoint[:endpoint.index('/', 1) + 1]
        return endpoint
