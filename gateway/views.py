from urllib.error import URLError

from django.http import HttpResponse, Http404
from django.http import HttpResponse
from django.http.request import QueryDict
from rest_framework import permissions, views, viewsets
from rest_framework.authentication import get_authorization_header

from django_filters.rest_framework import DjangoFilterBackend

from pyswagger import App
from pyswagger.contrib.client.requests import Client

from . import exceptions
from . import models as gtm
from . import serializers
from . import utils


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
    permission_classes = (permissions.IsAuthenticated,)
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
            schema_urls = utils.get_swagger_urls(kwargs['service'])
        except exceptions.ServiceDoesNotExist as e:
            return HttpResponse(content=e.content,
                                status=e.status,
                                content_type=e.content_type)

        # load swagger json as a raw App and prepare it
        try:
            app = App.load(schema_urls[kwargs['service']])
        except URLError as error:
            raise URLError(f'Make sure that {schema_urls[kwargs["service"]]} '
                           'is accessible.') from error
        if app.raw.basePath == '/':
            getattr(app, 'raw').update_field('basePath', '')
        app.prepare()
        client = Client()

        # create and perform a service request
        try:
            req, resp = self._get_req_and_rep(app, request, **kwargs)
        except exceptions.EndpointNotFound:
            raise Http404()
        else:
            response = self._perform_service_request(request, client, req,
                                                     resp)

            return HttpResponse(content=response.raw,
                                status=response.status,
                                content_type='application/json')

    def _validate_incoming_request(self, request, **kwargs):
        """
        Do certain validations to the request before starting to create a
        new request to services
        """
        if (request.META['REQUEST_METHOD'] in ['PUT', 'PATCH', 'DELETE'] and
                kwargs['pk'] is None):
            raise exceptions.RequestValidationError(
                'The object ID is missing.', 400)

    def _get_req_and_rep(self, app, request, **kwargs):
        """
        It resolves the path that should be used by the gateway in the
        request based on model, service and foreign key and return a request
        and response object

        :param app: App object from pyswagger
        :param method: the method name of request
        :param data: a dictionary with data
        :param kwargs: info about request like obj's PK, service and model
        :return: a tuple with pyswagger Request and Response obj
        """
        pk = kwargs['pk']
        model = kwargs['model'] if kwargs.get('model') else ''
        method = request.META['REQUEST_METHOD'].lower()
        payload = request.data if hasattr(request, 'data') else dict()
        data = payload.dict() if isinstance(payload, QueryDict) else payload

        if request.content_type == 'application/json':
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

        if pk is None:
            # resolve the path
            path = '/%s/' % model
            path_item = app.s(path)

            # call operation
            if method == 'post':
                return getattr(path_item, method).__call__(**data)
            elif method == 'get':
                return getattr(path_item, method).__call__()
        elif pk is not None:
            try:
                int(pk)
            except ValueError:
                pk_name = 'uuid'
            else:
                pk_name = 'id'

            path = '/{0}/{{{1}}}/'.format(model, pk_name)
            try:
                path_item = app.s(path)
            except KeyError:
                raise exceptions.EndpointNotFound(path)
            data.update({
                pk_name: pk,
            })

            # call operation
            if method in ['put', 'patch']:
                return getattr(path_item, method).__call__(**data)
            elif method in ['get', 'delete']:
                return getattr(path_item, method).__call__(**data)

    def _get_service_request_headers(self, request):
        """
        Get all the headers that are necessary to redirect the request to
        the needed service

        :param request:
        :return: a dictionary with all the needed headers
        """
        # get the authorization header from current request
        authorization = get_authorization_header(request).decode('utf-8')

        # Add only Authorization header, PySwaager will handle the rest of it
        headers = {
            'Authorization': authorization,
        }
        return headers

    def _perform_service_request(self, request, client, req, resp):
        headers = self._get_service_request_headers(request)
        try:
            return client.request((req, resp), headers=headers)
        except Exception as e:
            error_msg = (f'An error occurred when redirecting the request to '
                         f'or receiving the response from the service.\n'
                         f'Origin: ({e.__class__.__name__}: {e})')
            raise exceptions.PySwaggerError(error_msg)
