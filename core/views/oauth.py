from rest_framework import mixins, viewsets
import django_filters
from oauth2_provider.models import AccessToken, Application, RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.contrib.auth import authenticate

from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework import status

from core.serializers import AccessTokenSerializer, ApplicationSerializer, RefreshTokenSerializer
from core.permissions import IsSuperUser
from core.utils import generate_access_tokens


class AccessTokenViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    """
    title:
    Users' access tokens

    description:
    An AccessToken instance represents the actual access token to access user's resources.

    retrieve:
    Return the given AccessToken.

    Return the given AccessToken.

    list:
    Return a list of all the existing AccessTokens.

    Return a list of all the existing AccessTokens.

    destroy:
    Delete an AccessToken instance.

    Delete an AccessToken instance.
    """

    filterset_fields = ('user__username',)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (IsSuperUser,)
    queryset = AccessToken.objects.all()
    serializer_class = AccessTokenSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    title:
    Clients on the authorization server

    description:
    An Application instance represents the actual access token to access user's resources.

    retrieve:
    Return the given Application.

    Return the given Application.

    list:
    Return a list of all existing Applications.

    Return a list of all existing Applications.

    create:
    Create a new Application instance.

    Create a new Application instance.

    update:
    Update an existing Application instance.

    Update an existing Application instance.

    destroy:
    Delete an existing Application instance.

    Delete an existing Application instance.
    """

    permission_classes = (IsSuperUser,)
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer


class RefreshTokenViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    """
    title:
    Users' refresh tokens

    description:
    A RefreshToken instance represents a token that can be swapped for a new access token when it expires.

    retrieve:
    Return the given RefreshToken.

    Return the given RefreshToken.

    list:
    Return a list of all the existing RefreshTokens.

    Return a list of all the existing RefreshTokens.

    destroy:
    Delete a RefreshToken instance.

    Delete a RefreshToken instance.
    """

    filterset_fields = ('user__username',)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (IsSuperUser,)
    queryset = RefreshToken.objects.all()
    serializer_class = RefreshTokenSerializer


class LoginView(APIView):
    permission_classes = [AllowAny,]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        client_id = request.data.get('client_id')

        if not (username and password and client_id):
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)

        if user is None:
            raise AuthenticationFailed("Invalid credentials")

        # Generate JWT token
        try:
            token_object = generate_access_tokens(request, user, client_id)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(token_object, status=status.HTTP_200_OK)
