import logging
import json

from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

from .exceptions import SocialAuthFailed, SocialAuthNotConfigured
from gateway.exceptions import PermissionDenied, EndpointNotFound, DataMeshError

logger = logging.getLogger(__name__)


class DisableCsrfCheck(MiddlewareMixin):
    def process_request(self, req):
        attr = '_dont_enforce_csrf_checks'
        if not getattr(req, attr, False):
            setattr(req, attr, True)


# TODO: Remove dependency to gateway and datamesh app making their exception classes inherit the core one
MIDDLEWARE_EXCEPTIONS = (
    PermissionDenied,
    EndpointNotFound,
    SocialAuthFailed,
    SocialAuthNotConfigured,
    DataMeshError,
)


class ExceptionMiddleware(MiddlewareMixin):
    @staticmethod
    def process_exception(request, exception):
        if isinstance(exception, MIDDLEWARE_EXCEPTIONS):
            return JsonResponse(
                data=json.loads(exception.content), status=exception.status
            )
        return None
