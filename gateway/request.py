import logging
import json
from urllib.error import URLError
from typing import Any, Dict, Tuple, Union, List

import requests
from bravado_core.spec import Spec
from django.http.request import QueryDict
from django.db.models import QuerySet, Q
from rest_framework.request import Request
from rest_framework.authentication import get_authorization_header

from . import exceptions
from . import utils
from .models import LogicModule
from datamesh.models import LogicModuleModel, JoinRecord, Relationship

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

    def __init__(self, request: Request, **kwargs):
        self.request = request
        self.url_kwargs = kwargs
        self._logic_modules = dict()
        self._specs = dict()
        self._data = dict()

    def perform(self) -> GatewayResponse:
        """
        Make request to underlying service(s) and returns aggregated response.
        """
        # init swagger spec from the service swagger doc file
        try:
            spec = self._get_swagger_spec(self.url_kwargs['service'])
        except exceptions.ServiceDoesNotExist as e:
            return GatewayResponse(e.content, e.status, {'Content-Type': e.content_type})

        return self._get_data(spec)

    def _get_logic_module(self, service_name: str) -> LogicModule:
        """
        Retrieve LogicModule by service name.
        """
        if service_name not in self._logic_modules:
            try:
                self._logic_modules[service_name] = LogicModule.objects.get(endpoint_name=service_name)
            except LogicModule.DoesNotExist:
                raise exceptions.ServiceDoesNotExist(f'Service "{service_name}" not found.')
        return self._logic_modules[service_name]

    def _get_swagger_spec(self, endpoint_name: str) -> Spec:
        """
        Get Swagger spec of specified service.
        """
        logic_module = self._get_logic_module(endpoint_name)
        schema_url = utils.get_swagger_url_by_logic_module(logic_module)

        config = {
            'validate_requests': False,
            'validate_responses': False,
            'use_models': False,
            'validate_swagger_spec': False,
        }

        if schema_url not in self._specs:
            try:
                response = requests.get(schema_url)
                spec_dict = response.json()
            except URLError:
                raise URLError(f'Make sure that {schema_url} is accessible.')

            swagger_spec = Spec.from_dict(spec_dict, config=config)
            self._specs[schema_url] = swagger_spec

        return self._specs[schema_url]

    def _get_data(self, spec):
        raise NotImplementedError('You need to implement this method')

    def is_valid_for_cache(self) -> bool:
        """ Checks if request is valid for caching operations """
        return self.request.method.lower() == 'get' and not self.request.query_params

    def get_request_data(self) -> dict:
        """
        Create the data structure to be used in Swagger request. GET and  DELETE
        requests don't require body, so the data structure will have just
        query parameters if passed to swagger request.

        :param rest_framework.Request request: request info
        :return dict: request body structured for PySwagger
        """
        if self.request.content_type == 'application/json':
            return json.dumps(self.request.data)

        method = self.request.META['REQUEST_METHOD'].lower()
        data = self.request.query_params.dict()

        data.pop('aggregate', None)
        data.pop('join', None)

        if method in ['post', 'put', 'patch']:
            query_dict_body = self.request.data if hasattr(self.request, 'data') else dict()
            body = query_dict_body.dict() if isinstance(query_dict_body, QueryDict) else query_dict_body
            data.update(body)

            # handle uploaded files
            if self.request.FILES:
                for key, value in self.request.FILES.items():
                    data[key] = {
                        'header': {
                            'Content-Type': value.content_type,
                        },
                        'data': value,
                        'filename': value.name,
                    }

        return data


class GatewayRequest(BaseGatewayRequest):
    """
    Allows to perform synchronous requests to underlying services with requests package
    """

    def _get_data(self, spec: Spec) -> GatewayResponse:

        # create and perform a service data request
        content, status_code, headers = self._data_request(spec=spec, **self.url_kwargs)

        # aggregate/join with the JoinRecord-models
        if 'join' in self.request.query_params and status_code == 200 and type(content) in [dict, list]:
            try:
                self._join_response_data(resp_data=content)
            except exceptions.ServiceDoesNotExist as e:
                logger.error(e.content)

        # TODO: old DataMesh aggregation should be here until it's replaced by the new DataMesh

        if type(content) in [dict, list]:
            content = json.dumps(content, cls=utils.GatewayJSONEncoder)

        return GatewayResponse(content, status_code, headers)

    def get_headers(self) -> dict:
        """Get data and headers from the incoming request."""
        headers = {
            'Authorization': get_authorization_header(self.request).decode('utf-8'),
        }
        if self.request.content_type == 'application/json':
            headers['content-type'] = 'application/json'
        return headers

    def _data_request(self, spec: Spec, **kwargs) -> Tuple[Any, int, Dict[str, str]]:
        """
        Perform request to the service, use Swagger spec for validating operation
        """

        # Parse URL kwargs
        pk = kwargs.get('pk')
        model = kwargs.get('model', '').lower()
        path_kwargs = {}
        if kwargs.get('pk') is None:
            path = f'/{model}/'
        else:
            pk_name = 'uuid' if utils.valid_uuid4(pk) else 'id'
            path_kwargs = {pk_name: pk}
            path = f'/{model}/{{{pk_name}}}/'

        # Check that operation is valid according to spec
        operation = spec.get_op_for_request(self.request.method, path)
        if not operation:
            raise exceptions.EndpointNotFound(f'Endpoint not found: {self.request.method} {path}')
        method = operation.http_method.lower()
        path_name = operation.path_name

        # Build URL for the operation to request data from the service
        url = spec.api_url.rstrip('/') + path_name
        for k, v in path_kwargs.items():
            url = url.replace(f'{{{k}}}', v)

        # Check request cache if applicable
        if self.is_valid_for_cache() and url in self._data:
            logger.debug(f'Taking data from cache: {url}')
            return self._data[url]

        # Make request to the service
        method = getattr(requests, method)
        try:
            response = method(url,
                              headers=self.get_headers(),
                              params=self.request.query_params,
                              data=self.get_request_data(),
                              files=self.request.FILES)
        except Exception as e:
            error_msg = (f'An error occurred when redirecting the request to '
                         f'or receiving the response from the service.\n'
                         f'Origin: ({e.__class__.__name__}: {e})')
            raise exceptions.GatewayError(error_msg)

        try:
            content = response.json()
        except ValueError:
            content = response.content
        return_data = (content, response.status_code, response.headers)

        # Cache data if request is cache-valid
        if self.is_valid_for_cache():
            self._data[url] = return_data

        return return_data

    def _join_response_data(self, resp_data: Union[dict, list]) -> None:
        """
        Aggregates data from the requested service and from related services.
        Uses DataMesh relationship model for this.

        :param rest_framework.Request request: incoming request info
        :param resp_data: initial response data
        :param kwargs: extra arguments ['service', 'model', 'pk']
        """
        service_name = self.url_kwargs['service']

        if isinstance(resp_data, dict):
            if 'results' in resp_data:
                # In case of pagination take 'results' as a items data
                resp_data = resp_data.get('results', None)

        logic_module = self._get_logic_module(service_name)

        # find out forwards relations through logic module from request as origin
        padding = self.request.path.index(f'/{logic_module.endpoint_name}')
        endpoint = self.request.path[len(f'/{logic_module.endpoint_name}')+padding:]
        endpoint = endpoint[:endpoint.index('/', 1) + 1]
        logic_module_model = LogicModuleModel.objects.get(
            logic_module=logic_module, endpoint=endpoint)
        relationships = self._get_relationships(logic_module_model)
        origin_lookup_field = logic_module_model.lookup_field_name

        if isinstance(resp_data, dict):
            # detailed view
            self._add_nested_data(resp_data, relationships, origin_lookup_field)
        elif isinstance(resp_data, list):
            # list view
            for data_item in resp_data:
                self._add_nested_data(data_item, relationships, origin_lookup_field)
        return

    @staticmethod
    def _get_relationships(logic_module_model: LogicModuleModel) -> List[Tuple[Relationship, bool]]:
        """
        Get relationships with direction.
        :param logic_module_model: The Logic Module Model for the relations
        :return list: list of tuples with relationship and \
            boolean for forward or reverse direction (True = forwards, False = backwards)
        """
        relationships = Relationship.objects.filter(
            Q(origin_model=logic_module_model) | Q(related_model=logic_module_model)
        )
        relationships_with_direction = list()
        for relationship in relationships:
            relationships_with_direction.append((relationship, relationship.origin_model == logic_module_model))
        return relationships_with_direction

    @staticmethod
    def _get_join_records(origin_pk: Any, relationship: Relationship, is_forward_relationship: bool) -> QuerySet:
        if utils.valid_uuid4(str(origin_pk)):
            pk_field = 'record_uuid'
        else:
            pk_field = 'record_id'
        if not is_forward_relationship:
            pk_field = 'related_' + pk_field
        filter_dict = {pk_field: str(origin_pk)}
        return JoinRecord.objects.filter(relationship=relationship).filter(**filter_dict)

    def _add_nested_data(self,
                         data_item: dict,
                         relationships: List[Tuple[Relationship, bool]],
                         origin_lookup_field: str) -> None:
        """
        Nest data retrieved from related services.
        """
        origin_pk = data_item.get(origin_lookup_field)
        if not origin_pk:
            raise exceptions.DataMeshError(
                f'DataMeshConfigurationError: lookup_field_name "{origin_lookup_field}" '
                f'not found in response.')
        for relationship, is_forward_lookup in relationships:
            join_records = self._get_join_records(origin_pk, relationship, is_forward_lookup)

            # now backwards get related objects through join_records
            if join_records:
                related_objects = []

                # find out if pk is id or uuid and prepare lookup according to direction
                if is_forward_lookup:
                    related_model = relationship.related_model
                    related_lookup_is_id = join_records[0].related_record_id is not None
                    related_record_field = 'related_record_id' if related_lookup_is_id else 'related_record_uuid'
                else:
                    related_model = relationship.origin_model
                    related_lookup_is_id = join_records[0].record_id is not None
                    related_record_field = 'record_id' if related_lookup_is_id else 'record_uuid'

                spec = self._get_swagger_spec(related_model.logic_module.name)

                for join_record in join_records:

                    # remove query_params from original request
                    self.request._request.GET = QueryDict(mutable=True)

                    request_kwargs = {
                        'pk': (str(getattr(join_record, related_record_field))),
                        'model': related_model.endpoint.strip('/'),
                        'method': self.request.META['REQUEST_METHOD'].lower(),
                        'service': related_model.logic_module.name,
                    }

                    # create and perform a service request
                    content, _, _ = self._data_request(spec=spec, **request_kwargs)
                    if isinstance(content, dict):
                        related_objects.append(dict(content))
                    else:
                        logger.error(f'No response data for join record (request params: {request_kwargs})')

                # aggregate
                data_item[relationship.key] = related_objects


class AsyncGatewayRequest(BaseGatewayRequest):
    """
    Allows to perform asynchronous requests to underlying services with asyncio and aiohttp package
    """

    def _get_data(self, spec: Spec) -> GatewayResponse:
        """
        Makes request to underlying service(s) and returns aggregated response
        """
        raise NotImplementedError('Not implemented yet')
