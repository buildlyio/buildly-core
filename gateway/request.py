import logging
import json
import asyncio
from urllib.error import URLError
from typing import Any, Dict, Union
import re

import aiohttp
from bravado_core.spec import Spec
from django.db.models import Q
from django.http.request import QueryDict
from rest_framework.request import Request

from datamesh.exceptions import DatameshConfigurationError
from gateway import exceptions
from gateway import utils
from core.models import LogicModule
from gateway.clients import SwaggerClient, AsyncSwaggerClient
from datamesh.services import DataMesh
from datamesh.models import JoinRecord, Relationship

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
            return GatewayResponse(e.content, e.status, {'Content-Type': e.content_type})

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
            self.delete_join_record(pk=self.url_kwargs['pk'])  # delete join record

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

        # print('self.request.data',self.request.data)
        # check the request method
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            # fetch datamesh logic module info for current request from datamesh
            self.datamesh_relationship, self.request_param = datamesh.fetch_datamesh_relationship()
            self.retrieve_relationship_data(datamesh_relationship=self.datamesh_relationship, query_params=query_params, request_param=self.request_param, resp_data=resp_data)

        for service in datamesh.related_logic_modules:
            spec = self._get_swagger_spec(service)
            client_map[service] = SwaggerClient(spec, self.request)

        # self.request.method = 'GET'
        datamesh.extend_data(resp_data, client_map)

    def retrieve_relationship_data(self, datamesh_relationship: any, query_params: str, request_param: any, resp_data: Union[dict, list]):
        # iterate over the datamesh relationships
        # print('datamesh_relationship', datamesh_relationship)
        relationship_data = {}
        for relationship in datamesh_relationship:  # retrieve relationship data from request.data
            relationship_data[relationship] = self.request.data.get(relationship)

        for relationship, data in relationship_data.items():  # iterate over the relationship and data
            print('relationship--->', relationship)
            if not data:
                self.validate_relationship_data(relationship=relationship, resp_data=resp_data)
                continue

            # iterate over the relationship data as the data always in list
            for instance in data:
                # clearing all the form current request and updating it with related data the going to POST/PUT
                request_relationship_data = self.request  # copy the request data to another variable
                request_relationship_data.data.clear()  # clear request.data.data
                request_relationship_data.data.update(instance)  # update the relationship_data to request.data to perform request

                # validate request
                self.validate_request(resp_data=resp_data, request_param=request_param, relationship=relationship,
                                      query_params=query_params, relationship_data=request_relationship_data
                                      )

    def validate_request(self, resp_data: any, request_param: any, relationship: any, query_params: any, relationship_data: any):
        # get organization
        organization = self.request.session.get('jwt_organization_uuid', None)
        origin_model_pk_name = request_param[relationship]['origin_model_pk_name']
        related_model_pk_name = request_param[relationship]['related_model_pk_name']
        request_method = self.request.method

        # post the origin_model model data and create join with related_model
        if self.request.method in ['POST'] and 'extend' in query_params:
            origin_model_pk = resp_data[origin_model_pk_name]
            related_model_pk = self.request.data[related_model_pk_name]
            self.join_record(relationship=relationship, origin_model_pk=origin_model_pk, related_model_pk=related_model_pk, organization=organization)

        # update the created object reference to request_relationship_data
        if self.request.method in ['POST'] and 'join' in query_params:
            relationship_data.data[related_model_pk_name] = resp_data.get(related_model_pk_name, None)

        # for the PUT/PATCH request update PK in request param
        if self.request.method in ['PUT', 'PATCH'] and 'join' in query_params:
            # assuming if request doesn't have pk then data needed to be created
            pk = relationship_data.data.get(origin_model_pk_name, None)
            if not pk:
                # validation for to save reference of related model
                reference_field_name = related_model_pk_name if relationship_data.data.get(related_model_pk_name) else re.split("_", related_model_pk_name)[0]

                if relationship_data.data[reference_field_name]:
                    # update the method as we are creating relation object and save pk to none as we are performing post request
                    request_param[relationship]['pk'], self.request.method = None, 'POST'
                    relationship_data.data[reference_field_name] = resp_data[related_model_pk_name]
            else:
                # update the request and param method here we are keeping original request in
                # request_method considering request might update for above condition
                self.request.method, request_param[relationship]['method'] = request_method, request_method
                request_param[relationship]['pk'] = pk

                if 'join' in relationship_data.data:
                    pass

        # perform request
        self.perform_request(resp_data=resp_data, request_param=request_param, relationship=relationship,
                             query_params=query_params, request_relationship_data=relationship_data, organization=organization)

    def perform_request(self, resp_data: any, request_param: any, relationship: any, query_params: any, request_relationship_data: any, organization: any):
        # allow only if origin model needs to update or create
        if self.request.method in ['POST', 'PUT', 'PATCH'] and 'join' in query_params:
            # create a client for performing data requests
            spec = self._get_swagger_spec(request_param[relationship]['service'])
            client = SwaggerClient(spec, request_relationship_data)

            # perform a service data request
            content, status_code, headers = client.request(**request_param[relationship])

            if self.request.method in ['POST'] and 'join' in query_params:  # create join record
                origin_model_pk = content[request_param[relationship]['origin_model_pk_name']]
                related_model_pk = resp_data[request_param[relationship]['related_model_pk_name']]
                self.join_record(relationship=relationship, origin_model_pk=origin_model_pk, related_model_pk=related_model_pk,
                                 organization=organization)

    def validate_relationship_data(self, resp_data: any, relationship: any):
        """This function will validate the type of field and the relationship data"""
        origin_lookup_field_uuid = resp_data[self.request_param[relationship]['origin_lookup_field_name']]
        related_lookup_field_uuid = resp_data[self.request_param[relationship]['related_lookup_field_name']]

        if related_lookup_field_uuid:
            if type(related_lookup_field_uuid) == type([]):  # check for array type
                for uuid in related_lookup_field_uuid:  # for each item in array/list
                    related_lookup_field_uuid = uuid
                    # validate the join
                    self.validate_join(record_uuid=origin_lookup_field_uuid, related_record_uuid=related_lookup_field_uuid, relationship=relationship)
            else:
                self.validate_join(record_uuid=origin_lookup_field_uuid, related_record_uuid=related_lookup_field_uuid, relationship=relationship)

    def validate_join(self, record_uuid: any, related_record_uuid: any, relationship: any):
        """This function is validating the join if the join not created, yet then it will create the join """
        join_record_instance = JoinRecord.objects.filter(relationship__key=relationship, record_uuid=record_uuid, related_record_uuid=related_record_uuid)
        if not join_record_instance:
            self.join_record(relationship=relationship, origin_model_pk=record_uuid, related_model_pk=related_record_uuid, organization=None)

    def join_record(self, relationship: str, origin_model_pk: str, related_model_pk: str, organization: any) -> None:
        """This function will create datamesh join"""
        JoinRecord.objects.create(
            relationship=Relationship.objects.filter(key=relationship).first(),
            record_uuid=origin_model_pk,
            related_record_uuid=related_model_pk,
            organization_id=organization
        )

    def delete_join_record(self, pk: [str, int]) -> None:

        JoinRecord.objects.filter(Q(record_uuid__icontains=pk) | Q(related_record_uuid__icontains=pk)
                                  | Q(record_id__icontains=pk) | Q(related_record_id__icontains=pk)
                                  ).delete()


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
            # Use stored specification of the module
            spec_dict = logic_module.api_specification

            # Pull specification of the module from its service and store it
            if spec_dict is None:
                async with aiohttp.ClientSession() as session:
                    async with session.get(schema_url) as response:
                        try:
                            spec_dict = await response.json()
                        except aiohttp.ContentTypeError:
                            raise exceptions.GatewayError(
                                f'Failed to parse swagger schema from {schema_url}. Should be JSON.'
                            )
                    logic_module.api_specification = spec_dict
                    logic_module.save()
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
