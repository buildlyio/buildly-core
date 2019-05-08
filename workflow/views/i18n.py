from rest_framework import viewsets
import django_filters

from workflow.models import Internationalization
from workflow.serializers import InternationalizationSerializer
from workflow.permissions import IsSuperUserOrReadOnly


class InternationalizationViewSet(viewsets.ModelViewSet):
    """
    title:
    Translations for the application

    description:
    Translation file store for each supported front end language JSON  storage.  This is global file and used for
    every user and organization.

    retrieve:
    Return the Internationalization.

    list:
    Return a list of all the existing Internationalizations.

    create:
    Create a new Internationalization instance.
    """

    filterset_fields = ('language',)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (IsSuperUserOrReadOnly,)
    queryset = Internationalization.objects.all()
    serializer_class = InternationalizationSerializer
