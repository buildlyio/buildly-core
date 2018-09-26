import json
import logging
from django.conf import settings
from django.http import HttpResponse
from django.views.generic.base import TemplateView
from oauth2_provider.views.generic import ProtectedResourceView


from workflow.models import (CoreUser, CoreSites)

from workflow.serializers import (CoreUserSerializer, CountrySerializer,
                                  OrganizationSerializer)

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
        }
        core_user = CoreUser.objects.all().filter(user=user)
        if len(core_user) == 1:
            body["core_user"] = CoreUserSerializer(
                instance=core_user[0], context={'request': request}).data
            body["organization"] = OrganizationSerializer(
                instance=core_user[0].organization,
                context={'request': request}).data
            body["country"] = CountrySerializer(
                instance=core_user[0].country,
                context={'request': request}).data

        return HttpResponse(json.dumps(body))
