import logging

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from core.permissions import IsSuperUser
from core.models import LogicModule
from core.serializers import LogicModuleSerializer

from gateway import utils

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
    queryset = LogicModule.objects.all()
    serializer_class = LogicModuleSerializer

    @action(methods=['PUT'], url_path='specification', detail=True)
    def update_api_specification(self, request, *args, **kwargs):
        """
        Updates the API specification of given logic module
        """
        instance = self.get_object()
        schema_url = utils.get_swagger_url_by_logic_module(instance)

        response = utils.get_swagger_from_url(schema_url)
        spec_dict = response.json()
        data = {'api_specification': spec_dict}

        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
