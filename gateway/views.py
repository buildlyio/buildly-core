import json
import logging
import uuid
from urllib.error import URLError
from typing import Tuple, List


from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.http.request import QueryDict
from rest_framework import permissions, views, viewsets
from rest_framework.authentication import get_authorization_header
from rest_framework.request import Request

from django_filters.rest_framework import DjangoFilterBackend

from pyswagger import App
from pyswagger.contrib.client.requests import Client
from pyswagger.io import Response as PySwaggerResponse

from datamesh.models import LogicModuleModel, JoinRecord, Relationship
from datamesh import utils as datamesh_utils
from workflow.permissions import IsSuperUser

from . import exceptions
from . import models as gtm
from . import serializers
from . import utils

from workflow import models as wfm

logger = logging.getLogger(__name__)


class LogicModuleViewSet(viewsets.ModelViewSet):
    """
    title:
    LogicModule of the application

    description:

    retrieve:
    Return the LogicModule.

    list:
    Return a list of all the existing LogicModules.

    create:
    Create a new LogicModule instance.

    update:
    Update a LogicModule instance.

    delete:
    Delete a LogicModule instance.
    """

    filter_fields = ('name',)
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsSuperUser,)
    queryset = gtm.LogicModule.objects.all()
    serializer_class = serializers.LogicModuleSerializer


class APIGatewayView(views.APIView):
    """
    API gateway receives API requests, enforces throttling and security
    policies, passes requests to the back-end service and then passes the
    response back to the requester
    """

    permission_classes = (permissions.IsAuthenticated,)
    schema = None
    _logic_modules = None
    _data = None

    def __init__(self, *args, **kwargs):
        self._logic_modules = dict()
        self._data = dict()
        self.client = Client()
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
            return HttpResponse(content=e.content,
                                status=e.status,
                                content_type=e.content_type)

        # load Swagger resource file and init swagger client
        try:
            app = self._load_swagger_resource(kwargs['service'])
        except exceptions.ServiceDoesNotExist as e:
            logger.error(e.content)
            return HttpResponse(content=e.content,
                                status=e.status,
                                content_type=e.content_type)

        # create and perform a service request
        response = self._perform_service_request(
            app=app,
            request=request,
            **kwargs
        )

        # aggregate data if requested
        if request.query_params.get('aggregate', '_none').lower() == 'true':
            try:
                self._aggregate_response_data(
                    request=request,
                    response=response,
                    **kwargs
                )
            except exceptions.ServiceDoesNotExist as e:
                logger.error(e.content)

        # aggregate/join with the JoinRecord-models
        if request.query_params.get('join', None) is not None:
            try:
                self._join_response_data(
                    request=request,
                    response=response,
                    **kwargs
                )
            except exceptions.ServiceDoesNotExist as e:
                logger.error(e.content)

        if response.data is not None:
            content = json.dumps(response.data, cls=utils.GatewayJSONEncoder)
        else:
            content = response.raw

        content_type = ''.join(response.header.get('Content-Type', []))
        return HttpResponse(content=content, status=response.status, content_type=content_type)

    def _get_logic_module(self, service_name: str) -> gtm.LogicModule:
        if service_name not in self._logic_modules:
            try:
                self._logic_modules[service_name] = gtm.LogicModule.objects.get(endpoint_name=service_name)
            except gtm.LogicModule.DoesNotExist:
                raise exceptions.ServiceDoesNotExist(f'Service "{service_name}" not found.')
        return self._logic_modules[service_name]

    def _join_response_data(self, request: Request, response: PySwaggerResponse, **kwargs) -> None:
        """
        Same like: _aggregate_response_data, but this method uses the new Data Mesh
        models instead of the LogicModule.relationship - field.

        Aggregate data from first response.

        :param rest_framework.Request request: incoming request info
        :param PySwaggerResponse response: fist response
        :param kwargs: extra arguments ['service', 'model', 'pk']
        :return PySwaggerResponse: response with expanded data
        """
        service_name = kwargs['service']

        resp_data = response.data
        if isinstance(resp_data, dict):
            if 'results' in resp_data:
                # In case of pagination take 'results' as a items data
                resp_data = resp_data.get('results', None)

        logic_module = self._get_logic_module(service_name)

        # find out forwards relations through logic module from request as origin
        endpoint = request.path[len(f'/{logic_module.endpoint_name}'):]
        endpoint = endpoint[:endpoint.index('/', 1) + 1]
        logic_module_model = LogicModuleModel.objects.prefetch_related('joins_origins')\
            .get(logic_module=logic_module, endpoint=endpoint)
        relationships = logic_module_model.get_relationships()
        origin_lookup_field = logic_module_model.lookup_field_name

        if isinstance(resp_data, dict):
            # detailed view
            self._add_nested_data(request, resp_data, relationships, origin_lookup_field)
        elif isinstance(resp_data, list):
            # list view
            for data_item in resp_data:
                self._add_nested_data(request, data_item, relationships, origin_lookup_field)

        return

    def _add_nested_data(self,
                         request: Request,
                         data_item: dict,
                         relationships: List[Tuple[Relationship, bool]],
                         origin_lookup_field: str) -> None:
        """ Nests data retrieved from related services """
        origin_pk = data_item.get(origin_lookup_field)
        if not origin_pk:
            raise exceptions.DataMeshError(
                f'DataMeshConfigurationError: lookup_field_name "{origin_lookup_field}" '
                f'not found in response.')
        for relationship, is_forward_lookup in relationships:
            join_records = JoinRecord.objects.get_join_records(origin_pk, relationship, is_forward_lookup)

            # now backwards get related objects through join_records
            if join_records:
                related_objects = []

                related_model, related_record_field = datamesh_utils.prepare_lookup_kwargs(
                    is_forward_lookup, relationship, join_records[0])

                app = self._load_swagger_resource(related_model.logic_module.name)

                for join_record in join_records:

                    # remove query_params from original request
                    request._request.GET = QueryDict(mutable=True)

                    request_kwargs = {
                        'pk': (str(getattr(join_record, related_record_field))),
                        'model': related_model.endpoint.strip('/'),
                        'method': request.META['REQUEST_METHOD'].lower()
                    }

                    # create and perform a service request
                    response = self._perform_service_request(
                        app=app,
                        request=request,
                        **request_kwargs
                    )
                    if response.data:
                        related_objects.append(dict(response.data))
                    else:
                        logger.error(f'No response data for join record (request params: {request_kwargs})')

                # aggregate
                data_item[relationship.key] = related_objects

    def _aggregate_response_data(self, request: Request, response: PySwaggerResponse, **kwargs):
        """
        Aggregate data from first response

        :param rest_framework.Request request: incoming request info
        :param PySwaggerResponse response: fist response
        :param kwargs: extra arguments ['service', 'model', 'pk']
        :return PySwaggerResponse: response with expanded data
        """
        service_name = kwargs['service']

        resp_data = response.data
        if isinstance(resp_data, dict):
            if 'results' in resp_data:
                # DRF API payload structure
                resp_data = resp_data.get('results', None)

        logic_module = self._get_logic_module(service_name)

        # TODO: Implement depth validation
        # TODO: Implement authorization when retrieve Bifrost data
        if isinstance(resp_data, list):
            for data in resp_data:
                extension_map = self._generate_extension_map(
                    logic_module=logic_module,
                    model_name=kwargs['model'],
                    data=data
                )
                r = self._expand_data(request, extension_map)
                data.update(**r)
        elif isinstance(resp_data, dict):
            extension_map = self._generate_extension_map(
                logic_module=logic_module,
                model_name=kwargs['model'],
                data=resp_data
            )
            r = self._expand_data(request, extension_map)
            resp_data.update(**r)

    def _get_bifrost_uuid_name(self, model):
        # TODO: Remove this once all bifrost.models have only one `uuid`-field
        for field in model._meta.fields:
            if field.name.endswith('uuid') and field.unique and \
                    field.default == uuid.uuid4:
                return field.name

    def _expand_data(self, request: Request, extend_models: list):
        """
        Use extension maps to fetch data from different services and
        replace the relationship key by real data.

        :param Request request: incoming request
        :param list extend_models: list of dicts with relationships info
        :return dict: relations with their data
        """
        result = dict()
        for extend_model in extend_models:
            data = None
            if extend_model['service'] == 'bifrost':
                if hasattr(wfm, extend_model['model']):
                    cls = getattr(wfm, extend_model['model'])
                    uuid_name = self._get_bifrost_uuid_name(cls)
                    lookup = {
                        uuid_name: extend_model['pk']
                    }
                    try:
                        obj = cls.objects.get(**lookup)
                    except cls.DoesNotExist as e:
                        logger.info(e)
                    except ValueError:
                        logger.info(f' Not found: {extend_model["model"]} with'
                                    f' uuid_name={extend_model["pk"]}')
                    else:
                        utils.validate_object_access(request, obj)
                        data = model_to_dict(obj)
            else:
                app = self._load_swagger_resource(
                    extend_model['service']
                )

                # remove query_params from original request
                request._request.GET = QueryDict(mutable=True)

                # create and perform a service request
                res = self._perform_service_request(
                    app=app,
                    request=request,
                    **extend_model
                )
                data = res.data

            if data is not None:
                result[extend_model['relationship_key']] = data

        return result

    def _generate_extension_map(self, logic_module: gtm.LogicModule, model_name: str, data: dict):
        """
        Generate a list of relationship map of a specific service model.

        :param LogicModule logic_module: a logic module instance
        :param str model_name: Model name that should expand the relationships
        :param dict data: response data from first request
        :return list: list of dicts with relationships info
        """
        extension_map = []
        if not logic_module.relationships:
            logger.warning(f'Tried to aggregate but no relationship defined '
                           f'in {logic_module}.')
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

    def _load_swagger_resource(self, endpoint_name: str):
        """
        Get Swagger spec of specified service and create an app instance to
        be able to validate requests/responses and perform request.

        :param endpoint_name: name of the service endpoint that data will be retrieved
        :return PySwagger.App: an app instance
        """
        # load Swagger resource file

        logic_module = self._get_logic_module(endpoint_name)
        schema_url = utils.get_swagger_url_by_logic_module(logic_module)

        if schema_url not in self._data:
            # load swagger json as a raw App and prepare it
            try:
                app = App.load(schema_url)
            except URLError:
                raise URLError(
                    f'Make sure that {schema_url} is accessible.')
            if app.raw.basePath == '/':
                getattr(app, 'raw').update_field('basePath', '')
            app.prepare()
            self._data[schema_url] = app

        return self._data[schema_url]

    def _validate_incoming_request(self, request, **kwargs):
        """
        Do certain validations to the request before starting to create a
        new request to services

        :param rest_framework.Request request: request info
        :param kwargs: info about request like obj's PK, service and model
        """
        if (request.META['REQUEST_METHOD'] in ['PUT', 'PATCH', 'DELETE'] and
                kwargs['pk'] is None):
            raise exceptions.RequestValidationError(
                'The object ID is missing.', 400)

    def _get_swagger_data(self, request):
        """
        Create the data structure to be used in PySwagger. GET and  DELETE
        requests don't required body, so the data structure will have just
        query parameter if passed.

        :param rest_framework.Request request: request info
        :return dict: request body structured for PySwagger
        """
        method = request.META['REQUEST_METHOD'].lower()
        data = request.query_params.dict()

        # remove specific gateway query params
        if data.get('aggregate', None):
            data.pop('aggregate')
        if data.get('join', None) is not None:
            data.pop('join')

        if method in ['post', 'put', 'patch']:
            qd_body = request.data if hasattr(request, 'data') else dict()
            body = (qd_body.dict() if isinstance(qd_body, QueryDict) else
                    qd_body)
            data.update(body)

            if request.content_type == 'application/json' and data:
                data = {
                    'data': data
                }

            # handle uploaded files
            if request.FILES:
                for key, value in request.FILES.items():
                    data[key] = {
                        'header': {
                            'Content-Type': value.content_type,
                        },
                        'data': value,
                        'filename': value.name,
                    }

        return data

    def _get_req_and_rep(self, app, request, **kwargs):
        """
        It resolves the path that should be used by the gateway in the
        request based on model, service and foreign key and return a request
        and response object

        :param app: App object from pyswagger
        :param rest_framework.Request request: request info
        :param kwargs: info about request like obj's PK, service and model
        :return: a tuple with pyswagger Request and Response obj
        """
        pk = kwargs.get('pk')
        model = kwargs.get('model', '').lower()
        method = request.META['REQUEST_METHOD'].lower()
        data = self._get_swagger_data(request)

        if pk is None:
            # resolve the path
            path = '/%s/' % model
            path_item = app.s(path)
        else:
            if utils.valid_uuid4(pk):
                pk_name = 'uuid'
            else:
                pk_name = 'id'
            # evaluates to '/siteprofiles/uuid/' or '/siteprofiles/id/'
            path = '/{0}/{{{1}}}/'.format(model, pk_name)
            data.update({pk_name: pk})
            try:
                path_item = app.s(path)
            except KeyError:
                raise exceptions.EndpointNotFound(f'Endpoint not found: {method.upper()} {path}')

        # call operation
        if not (hasattr(path_item, method) and callable(getattr(path_item, method))):
            raise exceptions.EndpointNotFound(f'Endpoint not found: {method.upper()} {path}')
        return getattr(path_item, method).__call__(**data)

    def _get_service_request_headers(self, request):
        """
        Get all the headers that are necessary to redirect the request to
        the needed service

        :param rest_framework.Request request: request info
        :return: a dictionary with all the needed headers
        """
        # get the authorization header from current request
        authorization = get_authorization_header(request).decode('utf-8')

        # Add only Authorization header, PySwagger will handle the rest of it
        headers = {
            'Authorization': authorization,
        }
        return headers

    def _perform_service_request(self, app: App, request: Request, **kwargs):
        """
        Perform request to the service using the PySwagger client.

        :param pyswagger.App app: an instance of App
        :param rest_framework.Request request: incoming request info
        :return pyswagger.Response: response from the service
        """
        req, resp = self._get_req_and_rep(app, request, **kwargs)

        req.prepare(handle_files=False)  # prepare request to get URL from it for checking cache
        key_url = req.url

        if request.META['REQUEST_METHOD'].lower() == 'get' and key_url in self._data:
            # Caching is only for GET requests
            return self._data[key_url]
        else:
            headers = self._get_service_request_headers(request)
            try:
                data = self.client.request((req, resp), headers=headers)
            except Exception as e:
                error_msg = (f'An error occurred when redirecting the request to '
                             f'or receiving the response from the service.\n'
                             f'Origin: ({e.__class__.__name__}: {e})')
                raise exceptions.PySwaggerError(error_msg)
            if request.META['REQUEST_METHOD'].lower() == 'get':
                # Cache only GET requests
                self._data[key_url] = data
            return data
