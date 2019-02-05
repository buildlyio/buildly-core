import logging

from urllib.error import URLError

from django.forms.models import model_to_dict
from django.http import HttpResponse, Http404
from django.http.request import QueryDict
from rest_framework import permissions, views, viewsets
from rest_framework.authentication import get_authorization_header
from rest_framework.request import Request

from django_filters.rest_framework import DjangoFilterBackend

from pyswagger import App
from pyswagger.contrib.client.requests import Client
from pyswagger.io import Response as PySwaggerResponse

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
            app = self._load_swagger_resource(
                kwargs['service']
            )
        except exceptions.ServiceDoesNotExist as e:
            logger.error(e.content)
            return HttpResponse(content=e.content,
                                status=e.status,
                                content_type=e.content_type)
        client = Client()

        # create and perform a service request
        response = self._perform_service_request(
            app=app,
            request=request,
            client=client,
            **kwargs
        )

        # aggregate data if requested
        if request.query_params.get('aggregate', None) == 'true':
            try:
                self._aggregate_response_data(
                    request=request,
                    response=response,
                    client=client,
                    **kwargs
                )
            except exceptions.ServiceDoesNotExist as e:
                logger.error(e.content)

        content = utils.json_dump(response.data)

        return HttpResponse(content=content,
                            status=response.status,
                            content_type='application/json')

    def _aggregate_response_data(self, request: Request,
                                 response: PySwaggerResponse,
                                 client: Client,
                                 **kwargs):
        """
        Aggregate data from first response

        :param rest_framework.Request request: incoming request info
        :param PySwaggerResponse response: fist response
        :param pyswagger.Client client: client based on requests
        :param kwargs: extra arguments ['service', 'model', 'pk']
        :return PySwaggerResponse: response with expanded data
        """
        service_name = kwargs['service']

        if isinstance(response.data, dict):
            if 'results' in response.data:
                # DRF API payload structure
                resp_data = response.data.get('results', None)
            else:
                resp_data = response.data
        else:
            resp_data = response.data

        try:
            logic_module = gtm.LogicModule.objects.get(name=service_name)
        except gtm.LogicModule.DoesNotExist:
            msg = 'Service "{}" not found.'.format(service_name)
            raise exceptions.ServiceDoesNotExist(msg)

        # TODO: Implement depth validation
        # TODO: Implement authorization when retrieve Bifrost data
        if isinstance(resp_data, list):
            for data in resp_data:
                extension_map = self._generate_extension_map(
                    logic_module=logic_module,
                    model_name=kwargs['model'],
                    data=data
                )
                r = self._expand_data(request, client, extension_map)
                data.update(**r)
        elif isinstance(resp_data, dict):
            extension_map = self._generate_extension_map(
                logic_module=logic_module,
                model_name=kwargs['model'],
                data=resp_data
            )
            r = self._expand_data(request, client, extension_map)
            resp_data.update(**r)

    def _expand_data(self, request: Request, client: Client,
                     extend_models: list):
        """
        Use extension maps to fetch data from different services and
        replace the relationship key by real data.

        :param Resquest request: incoming request
        :param Client client: client based on requests
        :param list extend_models: list of dicts with relationships info
        :return dict: relations with their data
        """
        result = dict()
        for extend_model in extend_models:
            data = None
            if extend_model['service'] == 'bifrost':
                if hasattr(wfm, extend_model['model']):
                    cls = getattr(wfm, extend_model['model'])
                    pk_name = cls._meta.pk.attname
                    lookup = {
                        pk_name: extend_model['pk']
                    }
                    try:
                        obj = cls.objects.get(**lookup)
                    except cls.DoesNotExist as e:
                        logger.info(e)
                    else:
                        data = model_to_dict(obj)
            else:
                app = self._load_swagger_resource(
                    extend_model['service']
                )

                # create and perform a service request
                res = self._perform_service_request(
                    app=app,
                    request=request,
                    client=client,
                    **extend_model
                )
                data = res.data

            if data is not None:
                result[extend_model['relationship_key']] = data

        return result

    def _generate_extension_map(self, logic_module: gtm.LogicModule,
                                model_name: str, data: dict):
        """
        Generate a list of relationship map of a specific service model.

        :param LogicModule logic_module: a logic module instance
        :param str model_name: Model name that should expand the relationships
        :param dict data: response data from first request
        :return list: list of dicts with relationships info
        """
        extension_map = []
        for k, v in logic_module.relationships[model_name].items():
            value = v.split('.')
            collection_args = {
                'service': value[0],
                'model': value[1],
                'pk': data[k],
                'relationship_key': k
            }
            extension_map.append(collection_args)

        return extension_map

    def _load_swagger_resource(self, service_name: str):
        """
        Get Swagger spec of specified service and create an app instance to
        be able to validate requests/responses and perform request.

        :param service_name: name of the service that data will be retrieved
        :return PySwagger.App: an app instance
        """
        # load Swagger resource file
        schema_urls = utils.get_swagger_urls(service_name)

        # load swagger json as a raw App and prepare it
        try:
            app = App.load(schema_urls[service_name])
        except URLError:
            raise URLError(
                f'Make sure that {schema_urls[service_name]} is accessible.')
        if app.raw.basePath == '/':
            getattr(app, 'raw').update_field('basePath', '')
        app.prepare()

        return app

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
        if data.get('depth', None):
            data.pop('depth')

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
        pk = kwargs['pk']
        model = kwargs['model'].lower() if kwargs.get('model') else ''
        method = request.META['REQUEST_METHOD'].lower()
        data = self._get_swagger_data(request)

        if pk is None:
            # resolve the path
            path = '/%s/' % model
            path_item = app.s(path)

            # call operation
            return getattr(path_item, method).__call__(**data)
        elif pk is not None:
            try:
                int(pk)
            except ValueError:
                pk_name = 'uuid'
            else:
                pk_name = 'id'

            # evaluates to '/siteprofiles/uuid/' or '/siteprofiles/id/'
            path = '/{0}/{{{1}}}/'.format(model, pk_name)
            data.update({pk_name: pk})
            try:
                path_item = app.s(path)
            except KeyError:
                raise exceptions.EndpointNotFound(path)

            # call operation
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

        # Add only Authorization header, PySwaager will handle the rest of it
        headers = {
            'Authorization': authorization,
        }
        return headers

    def _perform_service_request(self, app: App, request: Request,
                                 client: Client, **kwargs):
        """
        Perform request to the service using the PySwagger client.

        :param pyswagger.App app: an instance of App
        :param rest_framework.Request request: incoming request info
        :param pyswagger.Client client: client based on requests
        :return pyswagger.Response: response from the service
        """
        try:
            req, resp = self._get_req_and_rep(app, request, **kwargs)
        except exceptions.EndpointNotFound:
            raise Http404()

        headers = self._get_service_request_headers(request)
        try:
            return client.request((req, resp), headers=headers)
        except Exception as e:
            error_msg = (f'An error occurred when redirecting the request to '
                         f'or receiving the response from the service.\n'
                         f'Origin: ({e.__class__.__name__}: {e})')
            raise exceptions.PySwaggerError(error_msg)
