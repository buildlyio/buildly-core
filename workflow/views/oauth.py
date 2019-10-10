from rest_framework import mixins, viewsets
import django_filters

from oauth2_provider.models import AccessToken
from workflow.serializers import AccessTokenSerializer

from workflow.permissions import IsSuperUser


class AccessTokenViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    """
    title:
    Users' access tokens

    description:
    An AccessToken instance represents the actual access token to access user's resources.

    retrieve:
    Return the AccessToken.

    list:
    Return a list of all the existing AccessTokens.

    create:
    Create a new AccessToken instance.
    """

    filterset_fields = ('user__username',)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (IsSuperUser,)
    queryset = AccessToken.objects.all()
    serializer_class = AccessTokenSerializer
