from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.template import RequestContext
from social_core.exceptions import AuthFailed
from social_core.utils import (partial_pipeline_data, setting_url,
                               user_is_active, user_is_authenticated)
from social_django.utils import psa

from core.exceptions import SocialAuthFailed, SocialAuthNotConfigured
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt


def index(request):
    """View function for home page of site."""

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html')


"""
ERROR TEMPLATES and views
"""


def handler404(request, exception):
    context = RequestContext(request)
    err_code = f'404: {exception}'
    response = render_to_response('404.html', {"code": err_code}, context)
    response.status_code = 404
    return response
