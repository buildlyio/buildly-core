import typing
import logging
import json
from urllib.error import URLError

from django.http import HttpResponse
from django.http.request import QueryDict
from django.db.models import QuerySet
from rest_framework import permissions, views
from rest_framework.request import Request
from rest_framework.authentication import get_authorization_header
from bravado.requests_client import RequestsClient
from bravado.response import BravadoResponseMetadata

from . import exceptions
from . import utils
from .models import LogicModule
from .client import ExtendedSwaggerClient
from datamesh.models import LogicModuleModel, JoinRecord


logger = logging.getLogger(__name__)


class APIGatewayView(views.APIView):
    """
    API gateway receives API requests, enforces throttling and security
    policies, passes requests to the back-end service and then passes the
    response back to the requester
    """

    permission_classes = (permissions.IsAuthenticated,)
    schema = None

    def __init__(self, *args, **kwargs):
        self._logic_modules = dict()
        self._clients = dict()
        self._data = dict()
        self.http_client = RequestsClient()
        super().__init__(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.make_service_request(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.make_service_request(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.make_service_request(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.make_service_request(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.make_service_request(request, *args, **kwargs)

    def make_service_request(self, request, *args, **kwargs):
        """
        Create a request for the defined service
        """
        # validate incoming request before creating a service request
        try:
            self._validate_incoming_request(request, **kwargs)
        except exceptions.RequestValidationError as e:
            return HttpResponse(content=e.content, status=e.status, content_type=e.content_type)

        # load Swagger resource file and init swagger client
        try:
            client = self._get_swagger_client(kwargs['service'])
        except exceptions.ServiceDoesNotExist as e:
            logger.error(e.content)
            return HttpResponse(content=e.content, status=e.status, content_type=e.content_type)

        # create and perform a service request
        result, metadata = self._perform_service_request(client=client, request=request, **kwargs)

        # # aggregate data if requested
        # if request.query_params.get('aggregate', '_none').lower() == 'true':
        #     try:
        #         self._aggregate_response_data(
        #             request=request,
        #             response=response,
        #             **kwargs
        #         )
        #     except exceptions.ServiceDoesNotExist as e:
        #         logger.error(e.content)

        # aggregate/join with the JoinRecord-models
        if 'join' in request.query_params and type(result) in [dict, list]:
            try:
                self._join_response_data(request=request, resp_data=result, **kwargs)
            except exceptions.ServiceDoesNotExist as e:
                logger.error(e.content)

        if isinstance(result, dict) or isinstance(result, list):
            content = json.dumps(result, cls=utils.GatewayJSONEncoder)
        elif hasattr(result, 'text'):
            content = result.text
        else:
            raise exceptions.GatewayError('Invalid response from service')

        content_type = metadata.headers.get('Content-Type', '')
        return HttpResponse(content=content, status=metadata.status_code, content_type=content_type)

    def _validate_incoming_request(self, request: Request, **kwargs: dict) -> None:
        """
        Do certain validations to the request before starting to create a new request to services
        """
        if request.META['REQUEST_METHOD'] in ['PUT', 'PATCH', 'DELETE'] and kwargs['pk'] is None:
            raise exceptions.RequestValidationError('The object ID is missing.', 400)

    def _get_logic_module(self, service_name: str) -> LogicModule:
        """
        Retrieve LogicModule by service name
        """
        if service_name not in self._logic_modules:
            try:
                self._logic_modules[service_name] = LogicModule.objects.get(endpoint_name=service_name)
            except LogicModule.DoesNotExist:
                raise exceptions.ServiceDoesNotExist(f'Service "{service_name}" not found.')
        return self._logic_modules[service_name]

    def _get_swagger_client(self, endpoint_name: str) -> ExtendedSwaggerClient:
        """
        Get Swagger spec of specified service and create/get a Swagger Client instance to
        be able to validate requests/responses and perform request.
        """
        logic_module = self._get_logic_module(endpoint_name)
        schema_url = utils.get_swagger_url_by_logic_module(logic_module)

        config = {
            'validate_requests': False,
            'validate_responses': False,
            'use_models': False,
            'validate_swagger_spec': False,
        }

        if schema_url not in self._clients:
            try:
                client = ExtendedSwaggerClient.from_url(schema_url, http_client=self.http_client, config=config)
            except URLError:
                raise URLError(f'Make sure that {schema_url} is accessible.')
            self._clients[schema_url] = client

        return self._clients[schema_url]

    def _perform_service_request(self, client: ExtendedSwaggerClient, request: Request, **kwargs) \
            -> typing.Tuple[typing.Any, BravadoResponseMetadata]:
        """
        Perform request to the service using the Swagger client and returns response result and metadata
        """

        pk = kwargs.get('pk')
        model = kwargs.get('model', '').lower()
        op_kwargs = {}
        if kwargs.get('pk') is None:
            path = f'/{model}/'
        else:
            pk_name = 'uuid' if utils.valid_uuid4(pk) else 'id'
            op_kwargs = {pk_name: pk}
            path = f'/{model}/{{{pk_name}}}/'

        headers = {
            'Authorization': get_authorization_header(request).decode('utf-8'),
        }

        op_kwargs['_request_options'] = {
            'headers': headers
        }
        op_kwargs.update(utils.get_request_data(request))

        cache_key = utils.generate_cache_key(**kwargs)
        if utils.is_valid_for_cache(request) and cache_key in self._data:
            logger.warning(f'Taking data from cache: {cache_key}')
            return self._data[cache_key]
        else:
            try:
                response = client.call_operation(request.method, path, **op_kwargs).response()
            except Exception as e:
                error_msg = (f'An error occurred when redirecting the request to '
                             f'or receiving the response from the service.\n'
                             f'Origin: ({e.__class__.__name__}: {e})')
                raise exceptions.GatewayError(error_msg)

            # Cache data if request is cache-valid
            if utils.is_valid_for_cache(request):
                self._data[cache_key] = (response.result, response.metadata)

            return response.result, response.metadata

    def _join_response_data(self, request: Request, resp_data: typing.Union[dict, list], **kwargs) -> None:
        """
        Same like: _aggregate_response_data, but this method uses the new Data Mesh
        models instead of the LogicModule.relationship - field.

        Aggregate data from initial response.

        :param rest_framework.Request request: incoming request info
        :param resp_data: initial response data
        :param kwargs: extra arguments ['service', 'model', 'pk']
        """
        service_name = kwargs['service']

        if isinstance(resp_data, dict):
            if 'results' in resp_data:
                # In case of pagination take 'results' as a items data
                resp_data = resp_data.get('results', None)

        logic_module = self._get_logic_module(service_name)

        # find out forwards relations through logic module from request as origin
        padding = request.path.index(f'/{logic_module.endpoint_name}')
        endpoint = request.path[len(f'/{logic_module.endpoint_name}')+padding:]
        endpoint = endpoint[:endpoint.index('/', 1) + 1]
        logic_module_model = LogicModuleModel.objects.prefetch_related('joins_origins')\
            .get(logic_module=logic_module, endpoint=endpoint)
        relationships = logic_module_model.joins_origins.all()
        origin_lookup_field = logic_module_model.lookup_field_name

        if isinstance(resp_data, dict):
            # detailed view
            self._add_nested_data(request, resp_data, relationships, origin_lookup_field)
        elif isinstance(resp_data, list):
            # list view
            for data_item in resp_data:
                self._add_nested_data(request, data_item, relationships, origin_lookup_field)
        return

    def _add_nested_data(self, request: Request, data_item: dict, relationships: QuerySet,
                         origin_lookup_field: str) -> None:
        """ Nests data retrieved from related services """
        origin_pk = data_item.get(origin_lookup_field)
        if not origin_pk:
            raise exceptions.DataMeshError(
                f'DataMeshConfigurationError: lookup_field_name "{origin_lookup_field}" '
                f'not found in response.')
        for relationship in relationships:
            if utils.valid_uuid4(str(origin_pk)):
                join_records = JoinRecord.objects.filter(relationship=relationship).filter(record_uuid=str(origin_pk))
            else:
                join_records = JoinRecord.objects.filter(relationship=relationship).filter(record_id=str(origin_pk))

            # now backwards get related objects through join_records
            if join_records:
                related_objects = []
                for join_record in join_records:
                    related_model = relationship.related_model
                    client = self._get_swagger_client(related_model.logic_module.name)

                    # remove query_params from original request
                    request._request.GET = QueryDict(mutable=True)

                    request_kwargs = {
                        'pk': (str(join_record.related_record_id) if join_record.related_record_id is not None
                               else str(join_record.related_record_uuid)),
                        'model': related_model.endpoint.strip('/'),
                        'method': request.META['REQUEST_METHOD'].lower(),
                        'service': related_model.logic_module.name,
                    }

                    # create and perform a service request
                    result, metadata = self._perform_service_request(client=client, request=request, **request_kwargs)
                    if isinstance(result, dict):
                        related_objects.append(dict(result))
                    else:
                        logger.error(f'No response data for join record (request params: {request_kwargs})')

                # aggregate
                data_item[relationship.key] = related_objects
