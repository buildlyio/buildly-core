import json
import logging

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.template import RequestContext
from django.shortcuts import render_to_response

from oauth2_provider.views.generic import ProtectedResourceView
from social_core.exceptions import AuthFailed
from social_core.utils import (partial_pipeline_data, setting_url,
                               user_is_active, user_is_authenticated)
from social_django.utils import psa

from workflow.serializers import (CoreUserSerializer,
                                  OrganizationSerializer)

from .exceptions import SocialAuthFailed, SocialAuthNotConfigured
from .utils import generate_access_tokens

logger = logging.getLogger(__name__)


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        extra_context = {
            'documentation_url': settings.DOCUMENTATION_URL,
            'api_url': settings.API_URL,
        }
        context.update(extra_context)
        return context


class OAuthUserEndpoint(ProtectedResourceView):
    def get(self, request, *args, **kwargs):
        user = request.user
        body = {
            'username': user.username,
            'email': user.email,
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'core_user': CoreUserSerializer(instance=user, context={'request': request}).data,
            'organization': OrganizationSerializer(instance=user.organization, context={'request': request}).data
        }
        return HttpResponse(json.dumps(body))


@never_cache
@csrf_exempt
@psa()
def oauth_complete(request, backend, *args, **kwargs):
    """
    Authentication complete view used for Social Auth
    """

    code = request.GET.get('code', None)
    if code is None:
        raise SocialAuthFailed('Authorization code has to be provided.')

    request.backend.data['code'] = code
    is_authenticated = user_is_authenticated(request.user)
    user = request.user if is_authenticated else None

    partial = partial_pipeline_data(request.backend, user, *args, **kwargs)
    if partial:
        user = request.backend.continue_pipeline(partial)
        # clean partial data after usage
        request.backend.strategy.clean_partial_pipeline(partial.token)
    else:
        # check if social auth is configured properly
        if backend not in settings.SOCIAL_AUTH_LOGIN_REDIRECT_URLS:
            raise SocialAuthNotConfigured(f'The backend {backend} is not supported.')
        elif not settings.SOCIAL_AUTH_LOGIN_REDIRECT_URLS.get(backend):
            raise SocialAuthNotConfigured(f'A redirect URL for the backend {backend} was not defined.')

        # prepare request to validate code
        data = request.backend.strategy.request_data()
        data['code'] = code
        redirect_uri = settings.SOCIAL_AUTH_LOGIN_REDIRECT_URLS.get(backend)
        request.backend.redirect_uri = redirect_uri
        request.backend.STATE_PARAMETER = False
        request.backend.REDIRECT_STATE = False

        try:
            # validate code / trigger pipeline and return a user
            user = request.backend.complete(user=user, *args, **kwargs)
        except AuthFailed as e:
            raise SocialAuthFailed(e.args[0])

    if is_authenticated:
        # generate JWT/Bearer Token
        tokens = generate_access_tokens(request, user)
        return JsonResponse(data=tokens, status=200)
    elif user:
        if user_is_active(user):
            # generate JWT/Bearer Token
            tokens = generate_access_tokens(request, user)
            return JsonResponse(data=tokens, status=200)
        else:
            url = setting_url(request.backend, 'INACTIVE_USER_URL',
                              'LOGIN_ERROR_URL', 'LOGIN_URL')
    else:
        url = setting_url(request.backend, 'LOGIN_ERROR_URL', 'LOGIN_URL')

    return request.backend.strategy.redirect(url)


"""
404ERROR TEMPLATES and view
"""


def handler404(request):
    context = RequestContext(request)
    err_code = 404
    response = render_to_response('404.html', {"code": err_code}, context)
    response.status_code = 404
    return response
