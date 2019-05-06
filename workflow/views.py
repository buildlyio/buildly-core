"""
 TODO: We need to break this module into multiple modules in views package, it's already to large
"""
import logging
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.urls import resolve, Resolver404
import django_filters
from rest_framework import mixins, permissions, status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import CursorPagination, PageNumberPagination
import jwt
from chargebee import Plan, Subscription
from graphene_django.views import GraphQLView
from drf_yasg.utils import swagger_auto_schema


from workflow import models as wfm
from workflow.jwt_utils import create_invitation_token
from workflow.email_utils import send_email
from .permissions import (IsOrgMember, IsSuperUserOrReadOnly, CoreGroupsPermissions, AllowAuthenticatedRead,
                          AllowOnlyOrgAdmin)
from .swagger import (COREUSER_INVITE_RESPONSE, COREUSER_INVITE_CHECK_RESPONSE, COREUSER_RESETPASS_RESPONSE,
                      DETAIL_RESPONSE, SUCCESS_RESPONSE, TOKEN_QUERY_PARAM)
from . import serializers


logger = logging.getLogger(__name__)

User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class SmallResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50


class DefaultCursorPagination(CursorPagination):
    """
    TODO move this to settings to provide better standardization
    See http://www.django-rest-framework.org/api-guide/pagination/
    """
    page_size = 30
    max_page_size = 100
    page_size_query_param = 'page_size'


class WorkflowLevel1ViewSet(viewsets.ModelViewSet):
    """
    Workflow Level 1 is the primary building block for creating relational lists, navigation or generic use case objects
    in the application core.  A Workflow level 1 can have multiple related workflow level 2's and be associated with a
    specific organization or set for an entire application.

    title:
    Workflow Level 1 is the primary building block for creating relationships

    description:
    Workflow Level 1 is the primary building block for creating relational lists, navigation or generic use case objects
    in the application core.  A Workflow level 1 can have multiple related workflow level 2's and be associated with a
    specific organization or set for an entire application.

    retrieve:
    Return the given workflow.

    list:
    Return a list of all the existing workflows.

    create:
    Create a new workflow instance.
    """
    # Remove CSRF request verification for posts to this API
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(WorkflowLevel1ViewSet, self).dispatch(*args, **kwargs)

    def list(self, request, *args, **kwargs):
        # Use this queryset or the django-filters lib will not work
        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_global_admin:
            queryset = queryset.filter(organization_id=request.user.organization_id)

        paginate = request.GET.get('paginate')
        if paginate and (paginate.lower() == 'true' or paginate == '1'):
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)  # inherited from CreateModelMixin
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
<<<<<<< Updated upstream
        organization = self.request.user.organization
=======
        # TODO: Organization should be provided instead of using the first one
        organization = self.request.user.core_user.organizations.all().first()
>>>>>>> Stashed changes
        obj = serializer.save(organization=organization)
        obj.user_access.add(self.request.user)

    def destroy(self, request, *args, **kwargs):
        workflowlevel1 = self.get_object()
        workflowlevel1.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    ordering_fields = ('name',)
    ordering = ('name',)
    filterset_fields = ('name', 'level1_uuid')
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)

    queryset = wfm.WorkflowLevel1.objects.all()
    serializer_class = serializers.WorkflowLevel1Serializer
    permission_classes = (CoreGroupsPermissions, IsOrgMember)
    pagination_class = DefaultCursorPagination


class CoreGroupViewSet(viewsets.ModelViewSet):
    """
    CoreGroup is similar to Django Group, but it is associated with an organization.
    It's used for creating groups of Core Users inside an organization and defining model level permissions
    for this group
    """
    queryset = wfm.CoreGroup.objects.all()
    serializer_class = serializers.CoreGroupSerializer
    permission_classes = (CoreGroupsPermissions,)


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
        'default': serializers.CoreUserSerializer,
        'coreuser-invite': serializers.CoreUserInvitationSerializer,
        'coreuser-reset-password': serializers.CoreUserResetPasswordSerializer,
        'coreuser-reset-password-check': serializers.CoreUserResetPasswordCheckSerializer,
        'coreuser-reset-password-confirm': serializers.CoreUserResetPasswordConfirmSerializer,
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

    @swagger_auto_schema(methods=['post'],
                         request_body=serializers.CoreUserInvitationSerializer,
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

        organization = wfm.Organization.objects\
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
        registered_emails = User.objects.filter(email__in=email_addresses).values_list('email', flat=True)

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
                         request_body=serializers.CoreUserResetPasswordSerializer,
                         responses=COREUSER_RESETPASS_RESPONSE)
    @action(methods=['POST'], detail=False)
    def reset_password(self, request, *args, **kwargs):
        """
        This endpoint is used to request password resetting.
        It requests the Email field
        """
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
                         request_body=serializers.CoreUserResetPasswordCheckSerializer,
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
                         request_body=serializers.CoreUserResetPasswordConfirmSerializer,
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
        if self.request and self.request.method == 'POST':
            try:
                url_name = resolve(self.request.path).url_name
            except Resolver404:
                pass
            else:
                if url_name in self.SERIALIZERS_MAP:
                    return self.SERIALIZERS_MAP[url_name]

        return self.SERIALIZERS_MAP['default']

    def get_permissions(self):
        try:
            url_name = resolve(self.request.path).url_name
        except Resolver404:
            pass
        else:
            # different permissions when creating a new user or resetting password
            if self.request.method == 'POST' and url_name in ['coreuser-create',
                                                              'coreuser-reset-password',
                                                              'coreuser-reset-password-check',
                                                              'coreuser-reset-password-confirm']:
                return [permissions.AllowAny()]

            # different permissions for checking token
            if self.request.method == 'GET' and url_name == 'coreuser-invite-check':
                return [permissions.AllowAny()]

            # different permissions for the invitation process
            if self.request.method == 'POST' and url_name == 'coreuser-invite':
                return [AllowOnlyOrgAdmin()]

            # only org admin can update core user's data
            if self.request.method in ['PUT', 'PATCH'] and url_name == 'coreuser-detail':
                return [AllowOnlyOrgAdmin()]

        return super(CoreUserViewSet, self).get_permissions()

    filterset_fields = ('organization__id',)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    queryset = wfm.CoreUser.objects.all()
    permission_classes = (AllowAuthenticatedRead,)


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    Organization is a collection of CoreUsers An organization is also the primary relationship for a user.
    They are associated with an organization that then provides them access to join a workflow team.

    title:
    Organization is a collection of CoreUsers

    description:
    An organization is also the primary relationship for a user.
    They are associated with an organization that then provides them access to join a workflow team.

    retrieve:
    Return the given organization user.

    list:
    Return a list of all the organizations.

    create:
    Create a new organization instance.
    """

    def list(self, request, *args, **kwargs):
        # Use this queryset or the django-filters lib will not work
        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_global_admin:
            organization_id = request.user.organization_id
            queryset = queryset.filter(id=organization_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def subscription(self, request, pk):
        instance = self.get_object()
        try:
            result = Subscription.retrieve(instance.subscription_id)
            subscription = result.subscription
            result = Plan.retrieve(subscription.plan_id)
            plan = result.plan
        except Exception as e:
            logger.warning(e)
            return Response(
                {'detail': 'No subscription was found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            data = {
                'plan': {
                    'name': plan.name,
                },
                'status': subscription.status,
                'total_seats': subscription.plan_quantity,
                'used_seats': instance.used_seats
            }

            return Response(data, status=status.HTTP_200_OK)

    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (IsOrgMember,)
    queryset = wfm.Organization.objects.all()
    serializer_class = serializers.OrganizationSerializer


class WorkflowLevel2ViewSet(viewsets.ModelViewSet):
    """
    title:
    Workflow Level 2 is the secondary building block for creating relational lists, navigation or generic use case
    objects in the application core.

    description:
    A Workflow level 2 can have one parent workflow leve 1 and multiple related workflow
    level 2's and be associated with a specific organization or set for an entire application.

    retrieve:
    Return the given workflow level 2.

    list:
    Return a list of all the existing workflow level 2s.

    create:
    Create a new workflow level 2 instance.
    """
    # Remove CSRF request verification for posts to this API
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(WorkflowLevel2ViewSet, self).dispatch(*args, **kwargs)

    def list(self, request, *args, **kwargs):
        # Use this queryset or the django-filters lib will not work
        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_global_admin:
            organization_id = request.user.organization_id
            queryset = queryset.filter(workflowlevel1__organization_id=organization_id)

        paginate = request.GET.get('paginate')
        if paginate and (paginate.lower() == 'true' or paginate == '1'):
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(created_by=getattr(self.request.user, 'core_user', None))

    filterset_fields = ('level2_uuid', 'workflowlevel1__name', 'workflowlevel1__id')
    ordering = ('name',)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,
                       filters.OrderingFilter)
    queryset = wfm.WorkflowLevel2.objects.all()
    permission_classes = (CoreGroupsPermissions, IsOrgMember)
    serializer_class = serializers.WorkflowLevel2Serializer
    pagination_class = DefaultCursorPagination


class WorkflowLevel2SortViewSet(viewsets.ModelViewSet):
    """
    title:
    Workflow Level 2 sort is a JSON Array storage for the sort and ordering of workflow levels per organization

    description:
    Sort your workflowlevels in the JSON array. WARNING ensure that the JSON array relationships already exist
    in the workflow level 2 parent_id and Workflow level 1

    retrieve:
    Return the given workflow level 2 sort.

    list:
    Return a list of all the existing workflow level 2 sorts.

    create:
    Create a new workflow level 2 sort instance.
    """

    def list(self, request, *args, **kwargs):
        # Use this queryset or the django-filters lib will not work
        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_global_admin:
            user_groups = request.user.groups.values_list('name', flat=True)
            if wfm.ROLE_ORGANIZATION_ADMIN in user_groups:
                organization_id = request.user.organization_id
                queryset = queryset.filter(
                    workflowlevel1__organization_id=organization_id)
            else:
                wflvl1_ids = wfm.WorkflowTeam.objects.filter(
                    workflow_user=request.user).values_list(
                    'workflowlevel1__id', flat=True)
                queryset = queryset.filter(workflowlevel1__in=wflvl1_ids)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    queryset = wfm.WorkflowLevel2Sort.objects.all()
    permission_classes = (IsOrgMember,)
    serializer_class = serializers.WorkflowLevel2SortSerializer


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
    queryset = wfm.Internationalization.objects.all()
    serializer_class = serializers.InternationalizationSerializer


class WorkflowTeamViewSet(viewsets.ModelViewSet):
    """
    title:
    Workflow Team is the the permissions and access control for each workflow
    in the application core.

    description:
    A Workflow level team associates a user with a Group for permissions and workflow level 1
    for access to the entire workflow.

    retrieve:
    Return the given workflow team.

    list:
    Return a list of all the existing workflow teams.

    create:
    Create a new workflow team instance.
    """
    def list(self, request, *args, **kwargs):
        # Use this queryset or the django-filters lib will not work
        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_superuser:
            if wfm.ROLE_ORGANIZATION_ADMIN in request.user.groups.values_list(
                    'name', flat=True):
                organization_id = request.user.organization_id
                queryset = queryset.filter(
                    workflow_user__organization_id=organization_id)
            else:
                wflvl1_ids = wfm.WorkflowTeam.objects.filter(
                    workflow_user=request.user).values_list('workflowlevel1__id', flat=True)
                queryset = queryset.filter(workflowlevel1__in=wflvl1_ids)

        nested = request.GET.get('nested_models')
        if nested is not None and (nested.lower() == 'true' or nested == '1'):
            self.serializer_class = serializers.WorkflowTeamListFullSerializer

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    filterset_fields = ('workflowlevel1__organization__id',)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (CoreGroupsPermissions,)
    queryset = wfm.WorkflowTeam.objects.all()
    serializer_class = serializers.WorkflowTeamSerializer


<<<<<<< Updated upstream
=======
class MilestoneViewSet(viewsets.ModelViewSet):
    """
    title:
    Milestones are time bound relationships to workflow level 1 or 2

    description:
    A milestone can be associated with a workflow level 1 or 2 to provide additional time tracked goals for a workflow.
    This can be used for example in a project workflow to track high level goals across a set of workflows.

    retrieve:
    Return the given milestone.

    list:
    Return a list of all the existing milestones.

    create:
    Create a new milestone instance.
    """

    def list(self, request, *args, **kwargs):
        # Use this queryset or the django-filters lib will not work
        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_superuser:
            organization_id = wfm.CoreUser.objects. \
                values_list('organization_id', flat=True). \
                get(user=request.user)
            queryset = queryset.filter(organization_id=organization_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    permission_classes = (IsOrgMember,)
    queryset = wfm.Milestone.objects.all()
    serializer_class = serializers.MilestoneSerializer


class PortfolioViewSet(viewsets.ModelViewSet):
    """
    title:
    Portfolio provides organizational structure or groupings for workflows

    description:
    A portfolio can be associated with a workflow level 1 or 2 to provide additional
    organizational structure for a workflow.
    This can be used for example in a project workflow to collect multiple workflows into one folder
    or grouping or in a navigational grouping as a way to provide a secondary site or structure.

    retrieve:
    Return the given portfolio.

    list:
    Return a list of all the existing portfolios.

    create:
    Create a new portfolio instance.
    """

    def list(self, request, *args, **kwargs):
        # Use this queryset or the django-filters lib will not work
        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_superuser:
            organization_id = wfm.CoreUser.objects. \
                values_list('organization_id', flat=True). \
                get(user=request.user)
            queryset = queryset.filter(organization_id=organization_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)  # inherited from CreateModelMixin

        portfolio = wfm.Portfolio.objects.get(pk=serializer.data['id'])
        portfolio.organization = request.user.core_user.organizations.all().first()
        portfolio.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    permission_classes = (AllowCoreUserRoles, IsOrgMember)
    queryset = wfm.Portfolio.objects.all()
    serializer_class = serializers.PortfolioSerializer


>>>>>>> Stashed changes
"""
GraphQL views from Graphene
"""


class DRFAuthenticatedGraphQLView(GraphQLView):
    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super(GraphQLView, cls).as_view(*args, **kwargs)
        return view
