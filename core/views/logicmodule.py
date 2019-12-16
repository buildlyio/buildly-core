import logging

from rest_framework import viewsets

from django_filters.rest_framework import DjangoFilterBackend

from core.permissions import IsSuperUser
from core.models import LogicModule
from core.serializers import LogicModuleSerializer

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
