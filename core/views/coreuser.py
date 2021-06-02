from urllib.parse import urljoin

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
import django_filters
import jwt
from drf_yasg.utils import swagger_auto_schema
import calendar
import time
from core.models import CoreUser, Organization
from core.serializers import (CoreUserSerializer, CoreUserWritableSerializer, CoreUserInvitationSerializer,
                              CoreUserResetPasswordSerializer, CoreUserResetPasswordCheckSerializer,
                              CoreUserResetPasswordConfirmSerializer, CoreUserEmailAlertSerializer,
                              CoreUserProfileSerializer)

from core.permissions import AllowAuthenticatedRead, AllowOnlyOrgAdmin, IsOrgMember
from core.swagger import (COREUSER_INVITE_RESPONSE, COREUSER_INVITE_CHECK_RESPONSE, COREUSER_RESETPASS_RESPONSE,
                          DETAIL_RESPONSE, SUCCESS_RESPONSE, TOKEN_QUERY_PARAM)
from core.jwt_utils import create_invitation_token
from core.email_utils import send_email
import logging
# from twilio.rest import Client
logger = logging.getLogger(__name__)


class CoreUserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin, mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):
    """
    A core user is an extension of the default User object.  A core user is also the primary relationship for identity
    and access to a logged in user. They are associated with an organization, Group (for permission though WorkflowTeam)
    and WorkflowLevel 1 (again through WorkflowTeam)

    title:
    A core user is an extension of the default User object.

    description:
    A core user is also the primary relationship for identity and access to a logged in user.
    They are associated with an organization, Group (for permission though WorkflowTeam)
    and WorkflowLevel 1 (again through WorkflowTeam)

    retrieve:
    Return the given core user.

    list:
    Return a list of all the existing core users.

    create:
    Create a new core user instance.
    """

    SERIALIZERS_MAP = {
        'default': CoreUserSerializer,
        'create': CoreUserWritableSerializer,
        'update': CoreUserWritableSerializer,
        'partial_update': CoreUserWritableSerializer,
        'update_profile': CoreUserProfileSerializer,
        'invite': CoreUserInvitationSerializer,
        'reset_password': CoreUserResetPasswordSerializer,
        'reset_password_check': CoreUserResetPasswordCheckSerializer,
        'reset_password_confirm': CoreUserResetPasswordConfirmSerializer,
        'alert': CoreUserEmailAlertSerializer,
    }

    def list(self, request, *args, **kwargs):
        # Use this queryset or the django-filters lib will not work
        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_global_admin:
            organization_id = request.user.organization_id
            queryset = queryset.filter(organization_id=organization_id)
        serializer = self.get_serializer(
            instance=queryset, context={'request': request}, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        queryset = self.queryset
        user = get_object_or_404(queryset, pk=kwargs.get('pk'))
        serializer = self.get_serializer(instance=user, context={'request': request})
        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    def me(self, request, *args, **kwargs):
        """
        Gives you the user information based on the user token sent within the request.
        """
        user = request.user
        serializer = self.get_serializer(instance=user, context={'request': request})
        return Response(serializer.data)

    @swagger_auto_schema(methods=['post'],
                         request_body=CoreUserInvitationSerializer,
                         responses=COREUSER_INVITE_RESPONSE)
    @action(methods=['POST'], detail=False)
    def invite(self, request, *args, **kwargs):
        """
        This endpoint is used to invite multiple user at the same time.
        It's expected a list of email, for example:
        {
            'emails': ['john@example.com', 'paul@example.com']
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        links = self.perform_invite(serializer)

        return Response(
            {
                'detail': 'The invitations were sent successfully.',
                'invitations': links,
            },
            status=status.HTTP_200_OK)

    @swagger_auto_schema(methods=['get'],
                         responses=COREUSER_INVITE_CHECK_RESPONSE,
                         manual_parameters=[TOKEN_QUERY_PARAM])
    @action(methods=['GET'], detail=False)
    def invite_check(self, request, *args, **kwargs):
        """
        This endpoint is used to validate invitation token and return
        the information about email and organization
        """
        try:
            token = self.request.query_params['token']
        except KeyError:
            return Response({'detail': 'No token is provided.'},
                            status.HTTP_401_UNAUTHORIZED)
        try:
            decoded = jwt.decode(token, settings.SECRET_KEY,
                                 algorithms='HS256')
        except jwt.DecodeError:
            return Response({'detail': 'Token is not valid.'},
                            status.HTTP_401_UNAUTHORIZED)
        except jwt.ExpiredSignatureError:
            return Response({'detail': 'Token is expired.'},
                            status.HTTP_401_UNAUTHORIZED)

        if CoreUser.objects.filter(email=decoded['email']).exists():
            return Response({'detail': 'Token has been used.'},
                            status.HTTP_401_UNAUTHORIZED)

        organization = Organization.objects\
            .values('organization_uuid', 'name')\
            .get(organization_uuid=decoded['org_uuid']) \
            if decoded['org_uuid'] else None

        return Response({
            'email': decoded['email'],
            'organization': organization
        }, status=status.HTTP_200_OK)

    @transaction.atomic
    def perform_invite(self, serializer):

        reg_location = urljoin(settings.FRONTEND_URL,
                               settings.REGISTRATION_URL_PATH)
        reg_location = reg_location + '?token={}'
        email_addresses = serializer.validated_data.get('emails')
        user = self.request.user

        organization = user.organization
        registered_emails = CoreUser.objects.filter(email__in=email_addresses).values_list('email', flat=True)

        links = []
        for email_address in email_addresses:
            if email_address not in registered_emails:
                # create or update an invitation

                token = create_invitation_token(email_address, organization)

                # build the invitation link
                invitation_link = self.request.build_absolute_uri(
                    reg_location.format(token)
                )
                links.append(invitation_link)

                # create the used context for the E-mail templates
                context = {
                    'invitation_link': invitation_link,
                    'org_admin_name': user.name
                    if hasattr(user, 'coreuser') else '',
                    'organization_name': organization.name
                    if organization else ''
                }
                subject = 'Application Access'  # TODO we need to make this dynamic
                template_name = 'email/coreuser/invitation.txt'
                html_template_name = 'email/coreuser/invitation.html'
                send_email(email_address, subject, context, template_name, html_template_name)

        return links

    @swagger_auto_schema(methods=['post'],
                         request_body=CoreUserResetPasswordSerializer,
                         responses=COREUSER_RESETPASS_RESPONSE)
    @action(methods=['POST'], detail=False)
    def reset_password(self, request, *args, **kwargs):
        """
        This endpoint is used to request password resetting.
        It requests the Email field
        """
        logger.warning('EMAIL EVENT!')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        count = serializer.save()
        return Response(
            {
                'detail': 'The reset password link was sent successfully.',
                'count': count,
            },
            status=status.HTTP_200_OK)

    @swagger_auto_schema(methods=['post'],
                         request_body=CoreUserResetPasswordCheckSerializer,
                         responses=SUCCESS_RESPONSE)
    @action(methods=['POST'], detail=False)
    def reset_password_check(self, request, *args, **kwargs):
        """
        This endpoint is used to check that token is valid.
        """
        serializer = self.get_serializer(data=request.data)
        return Response(
            {
                'success': serializer.is_valid(),
            },
            status=status.HTTP_200_OK)

    @swagger_auto_schema(methods=['post'],
                         request_body=CoreUserResetPasswordConfirmSerializer,
                         responses=DETAIL_RESPONSE)
    @action(methods=['POST'], detail=False)
    def reset_password_confirm(self, request, *args, **kwargs):
        """
        This endpoint is used to change password if the token is valid
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'detail': 'The password was changed successfully.',
            },
            status=status.HTTP_200_OK)

    def get_serializer_class(self):
        action_ = getattr(self, 'action', 'default')
        return self.SERIALIZERS_MAP.get(action_, self.SERIALIZERS_MAP['default'])

    def get_permissions(self):
        if hasattr(self, 'action'):
            # different permissions when creating a new user or resetting password
            if self.action in ['create',
                               'reset_password',
                               'reset_password_check',
                               'reset_password_confirm',
                               'invite_check',
                               'update_profile']:
                return [permissions.AllowAny()]

            if self.action in ['update', 'partial_update', 'invite']:
                return [AllowOnlyOrgAdmin(), IsOrgMember()]
            if self.action in ['invite']:
                return [AllowOnlyOrgAdmin(), IsOrgMember()]

        return super(CoreUserViewSet, self).get_permissions()

    filterset_fields = ('organization__organization_uuid',)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    queryset = CoreUser.objects.all()
    permission_classes = (AllowAuthenticatedRead,)

    @swagger_auto_schema(methods=['post'],
                         request_body=CoreUserEmailAlertSerializer,
                         responses=SUCCESS_RESPONSE)
    @action(methods=['POST'], detail=False)
    def alert(self, request, *args, **kwargs):
        """
        a)Request alert message and uuid of organization
        b)Access user uuids for that respective organization
        c)Check if opted for email alert service
        d)Send Email to the user's email with alert message
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        org_uuid = request.data['organization_uuid']
        messages = request.data['messages']
        subject_line = request.data['subject_line']
        if subject_line is not None:
            subject = subject_line
        else:
            subject = 'Alert message for shipment'
        for message in messages:
            try:
                time_tuple = time.strptime(message['date_time'], "%Y-%m-%dT%H:%M:%S%z")
            except ValueError:
                time_tuple = time.strptime(message['date_time'], "%Y-%m-%dT%H:%M:%S.%f%z")
            time_format = calendar.timegm(time_tuple)
            message['date_time'] = time.ctime(time_format)
        context = {
            'messages': messages,
        }
        template_name = 'email/coreuser/shipment_alert.txt'
        html_template_name = 'email/coreuser/shipment_alert.html'
        core_users = CoreUser.objects.filter(organization__organization_uuid=org_uuid, email_alert_flag=True)
        for user in core_users:
            email_address = user.email
            send_email(email_address, subject, context, template_name, html_template_name)
        return Response(
            {
                'detail': 'The alert messages were sent successfully on email.',
            }, status=status.HTTP_200_OK)
        # This code is commented out as in future, It will need to impliment message service.
        # for phone in phones:
        #     phone_number = phone
        #     account_sid = os.environ['TWILIO_ACCOUNT_SID']
        #     auth_token = os.environ['TWILIO_AUTH_TOKEN']
        #     client = Client(account_sid, auth_token)
        #     message = client.messages.create(
        #                     body=alert_message,
        #                     from_='+15082068927',
        #                     to=phone_number
        #                 )
        #     print(message.sid)

    @action(detail=True, methods=['patch'], name='Update Profile')
    def update_profile(self, request, pk=None, *args, **kwargs):
        """
        Update a user Profile
        """
        # the particular user in CoreUser table
        user = self.get_object()
        serializer = CoreUserProfileSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
