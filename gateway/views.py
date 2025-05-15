import logging

from django.http import HttpResponse
from rest_framework import views
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated

from gateway import exceptions
from gateway.permissions import AllowLogicModuleGroup
from gateway.request import GatewayRequest, AsyncGatewayRequest

logger = logging.getLogger(__name__)

class APIGatewayView(views.APIView):
    """
    API gateway receives API requests, enforces throttling and security
    policies, passes requests to the back-end service and then passes the
    response back to the requester
    """

    permission_classes = (IsAuthenticated, AllowLogicModuleGroup)
    schema = None
    gateway_request_class = GatewayRequest

    def __init__(self, *args, **kwargs):
        self._logic_modules = dict()
        self._specs = dict()
        self._data = dict()
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

    def options(self, request, *args, **kwargs):
        return self.make_service_request(request, *args, **kwargs)

    def make_service_request(self, request, *args, **kwargs):
        """
        Create a request for the defined service
        """
        try:
            self._validate_incoming_request(request, **kwargs)
        except exceptions.RequestValidationError as e:
            return HttpResponse(
                content=e.content, status=e.status, content_type=e.content_type
            )

        gw_request = self.gateway_request_class(request, **kwargs)
        gw_response = gw_request.perform()

        return HttpResponse(
            content=gw_response.content,
            status=gw_response.status_code,
            content_type=gw_response.headers.get('Content-Type'),
        )

    def _validate_incoming_request(self, request: Request, **kwargs: dict) -> None:
        """
        Do certain validations to the request before starting to create a new request to services
        """
        if (
            request.META['REQUEST_METHOD'] in ['PUT', 'PATCH', 'DELETE']
            and kwargs.get('pk') is None
        ):
            raise exceptions.RequestValidationError('The object ID is missing.', 400)