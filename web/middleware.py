import logging
import json

from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

from gateway import exceptions


logger = logging.getLogger(__name__)


class DisableCsrfCheck(MiddlewareMixin):

    def process_request(self, req):
        attr = '_dont_enforce_csrf_checks'
        if not getattr(req, attr, False):
            setattr(req, attr, True)


PROCESSED_EXCEPTIONS = (
    exceptions.PermissionDenied,
    exceptions.EndpointNotFound,
    exceptions.DataMeshError,
)

class ExceptionMiddleware(MiddlewareMixin):

    @staticmethod
    def process_exception(request, exception):
        if isinstance(exception, PROCESSED_EXCEPTIONS):
            return JsonResponse(data=json.loads(exception.content),
                                status=exception.status)
        return None
