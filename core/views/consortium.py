import logging
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets
from core.models import Consortium
from core.serializers import ConsortiumSerializer
from core.permissions import AllowOnlyOrgAdmin

logger = logging.getLogger(__name__)


class ConsortiumViewSet(viewsets.ModelViewSet):
    """
    Consortium is group of custodians that enables sharing of data.

    title:
    Consortium

    description:
    A Consortium is collective group of custodians

    which are in turn associated with an organization.

    retrieve:
    Return the Consortium.

    list:
    Return a list of all the existing Consortiums.

    create:
    Create a new Consortium instance.

    update:
    Update a Consortium instance.

    delete:
    Delete a Consortium instance.
    """

    filter_fields = ('name',)
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (AllowOnlyOrgAdmin,)
    queryset = Consortium.objects.all()
    serializer_class = ConsortiumSerializer
