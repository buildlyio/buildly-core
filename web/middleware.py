import logging
from threading import current_thread

from django.http import HttpResponse
from django.template import Template, Context
from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import PermissionDenied

logger = logging.getLogger(__name__)
_current_users = {}


def get_user():
    """
    Request independent method to retrieve current user
    from objects with no access to the current request
    :return: The current user of the requesting thread
    """
    thread = current_thread()
    if thread not in _current_users:
        return None
    return _current_users[thread]


class TolaSecurityMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add user object to thread-dependent storage
        _current_users[current_thread()] = request.user

        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        Processes PermissionDenied Exceptions for model-level access control
        """
        logger.info("Middleware has caught an exception. exception={}".format(
                    exception.message), type(exception))

        if type(exception) == PermissionDenied:
            t = Template("{'error':'Permission Denied'}")
            response_html = t.render(Context({}))

            response = HttpResponse(response_html)
            response.status_code = 403
            return response


class TolaRedirectMiddleware(object):
    """
    Middleware to store redirects in the session until they are ready to be
    processed.

    Redirects with 'next' are overwritten by Social Auth during the process
    and have to be restored at the end of the Authentication pipeline.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # store the next value of the inital request in the session
        if 'next' in request.GET:
            request.session["redirect_after_login"] = request.GET['next']

        return self.get_response(request)


class DisableCsrfCheck(MiddlewareMixin):

    def process_request(self, req):
        attr = '_dont_enforce_csrf_checks'
        if not getattr(req, attr, False):
            setattr(req, attr, True)
