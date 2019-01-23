import logging
import urllib

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import django_filters
from rest_framework import mixins, status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.pagination import CursorPagination, PageNumberPagination


from workflow import models as wfm

from .permissions import (IsOrgMember, IsSuperUserOrReadOnly, AllowTolaRoles,
                          AllowAuthenticatedRead, AllowOnlyOrgAdmin,
                          PERMISSIONS_ADMIN, PERMISSIONS_ORG_ADMIN,
                          PERMISSIONS_PROGRAM_ADMIN, PERMISSIONS_PROGRAM_TEAM,
                          PERMISSIONS_VIEW_ONLY)
from . import serializers


logger = logging.getLogger(__name__)


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


class UserViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                  mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    User is the primary relationship for identity and access to a logged in user.
    They are associated with an
    organization, Group (for permission though WorkflowTeam) and WorkflowLevel 1 (again through WorkflowTeam)

    title:
    User is the primary relationship for identity and access to a logged in user.

    description:
    They are associated with an
    organization, Group (for permission though WorkflowTeam) and WorkflowLevel 1 (again through WorkflowTeam)

    retrieve:
    Return the given user.

    list:
    Return a list of all the existing users.

    create:
    Create a new user instance.
    """
    queryset = wfm.User.objects.all()
    serializer_class = serializers.UserSerializer

    def update(self, request, pk):
        user_groups = request.user.groups.values_list('name', flat=True)
        instance = self.get_object()
        user_org = wfm.CoreUser.objects.\
            values_list('organization_id', flat=True).\
            get(user=instance)
        request_user_org = wfm.CoreUser.objects. \
            values_list('organization_id', flat=True).\
            get(user=request.user)
        if request.user.is_superuser \
                or (wfm.ROLE_ORGANIZATION_ADMIN in user_groups and
                    user_org == request_user_org):

            serializer = self.get_serializer(instance,
                                             data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Groups are used for setting permission descriptions in Workflow Team.  They are associated with an
    a user (for permission though WorkflowTeam)

    title:
    Groups are used for setting permission descriptions in Workflow Team.

    description:
    Groups are used for setting permission descriptions in Workflow Team.  They are associated with an
    a user (for permission though WorkflowTeam)

    retrieve:
    Return the given group.

    list:
    Return a list of all the existing groups.

    create:
    Create a new group instance.
    """
    queryset = wfm.Group.objects.all()
    serializer_class = serializers.GroupSerializer


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

    def list(self, request):
        # Use this queryset or the django-filters lib will not work
        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_superuser:
            if wfm.ROLE_ORGANIZATION_ADMIN in request.user.groups.values_list(
                    'name', flat=True):
                organization_id = wfm.CoreUser.objects. \
                    values_list('organization_id', flat=True). \
                    get(user=request.user)
                queryset = queryset.filter(organization_id=organization_id)
            else:
                wflvl1_ids = wfm.WorkflowTeam.objects.filter(
                    workflow_user__user=request.user).values_list(
                    'workflowlevel1__id', flat=True)
                queryset = queryset.filter(id__in=wflvl1_ids)

        paginate = request.GET.get('paginate')
        if paginate and (paginate.lower() == 'true' or paginate == '1'):
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def _get_user_org_role(self, user):
        if user.is_superuser:
            return 'Admin'
        else:
            groups = user.groups.values_list('name', flat=True).filter(
                name__in=[wfm.ROLE_ORGANIZATION_ADMIN, wfm.ROLE_VIEW_ONLY])
            if len(groups) == 2:
                return wfm.ROLE_ORGANIZATION_ADMIN
            elif len(groups) == 1:
                return groups.first()
            else:
                return None

    def _get_permissions(self, user, role_org):
        permissions = []

        permissions_role = {
            'Admin': PERMISSIONS_ADMIN,
            wfm.ROLE_ORGANIZATION_ADMIN: PERMISSIONS_ORG_ADMIN,
            wfm.ROLE_PROGRAM_ADMIN: PERMISSIONS_PROGRAM_ADMIN,
            wfm.ROLE_PROGRAM_TEAM: PERMISSIONS_PROGRAM_TEAM,
            wfm.ROLE_VIEW_ONLY: PERMISSIONS_VIEW_ONLY,
        }

        if role_org:
            qs = wfm.WorkflowLevel1.objects.\
                values_list('id', 'level1_uuid').\
                filter(organization=user.core_user.organization).order_by('id')
        else:
            qs = wfm.WorkflowTeam.objects.\
                values_list('workflowlevel1_id',
                            'workflowlevel1__level1_uuid', 'role__name').\
                filter(workflow_user=user.core_user).\
                order_by('workflowlevel1_id')

        for wflvl1_info in qs:
            if role_org:
                permissions_details = permissions_role.get(role_org)
                wflvl1_id = wflvl1_info[0]
                wflvl1_uuid = wflvl1_info[1]
                role = role_org
            else:
                wflvl1_id, wflvl1_uuid, role = wflvl1_info
                permissions_details = permissions_role.get(role)
            permission = {
                'workflowlevel1_id': wflvl1_id,
                'workflowlevel1_uuid': wflvl1_uuid,
                'role': role,
            }
            permission.update(permissions_details)
            permissions.append(permission)

        return permissions

    @action(detail=False, methods=['GET'])
    def permissions(self, request):
        data = {}

        role_org = self._get_user_org_role(request.user)
        if role_org:
            data['role_org'] = role_org
        data['permissions'] = self._get_permissions(request.user, role_org)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)  # inherited from CreateModelMixin

        # Assign the user to multiple properties of the Program
        group_program_admin = Group.objects.get(name=wfm.ROLE_PROGRAM_ADMIN)
        wflvl1 = wfm.WorkflowLevel1.objects.get(
            level1_uuid=serializer.data['level1_uuid'])
        wfm.WorkflowTeam.objects.create(
            workflow_user=request.user.core_user, workflowlevel1=wflvl1,
            role=group_program_admin)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        organization = self.request.user.core_user.organization
        obj = serializer.save(organization=organization)
        obj.user_access.add(self.request.user.core_user)

    def destroy(self, request, pk):
        workflowlevel1 = self.get_object()
        workflowlevel1.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if (self.request and self.request.method == 'GET' and
                self.action == 'permissions'):
            return serializers.WorkflowLevel1PermissionsSerializer
        else:
            return serializers.WorkflowLevel1Serializer

    ordering_fields = ('name',)
    ordering = ('name',)
    filter_fields = ('name', 'level1_uuid')
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,
                       filters.OrderingFilter)

    queryset = wfm.WorkflowLevel1.objects.all()
    permission_classes = (AllowTolaRoles, IsOrgMember)
    pagination_class = DefaultCursorPagination


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
    def list(self, request):
        # Use this queryset or the django-filters lib will not work
        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_superuser:
            organization_id = wfm.CoreUser.objects.\
                values_list('organization_id', flat=True).\
                get(user=request.user)
            queryset = queryset.filter(organization_id=organization_id)
        serializer = self.get_serializer(
            instance=queryset, context={'request': request}, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.queryset
        user = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(instance=user,
                                         context={'request': request})
        return Response(serializer.data)

    @action(methods=['POST'], detail=False)
    def invite(self, request):
        """
        This endpoint is used to invite multiple user at the same time.
        It's expected a list of email, for example:
        {
            'emails': ['john@example.com', 'paul@example.com']
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_invite(serializer)

        return Response({
            'detail': 'The invitations were sent successfully.'},
            status=status.HTTP_200_OK)

    # WE MIGHT NEED TO MOVE THIS # TODO RESEARCH WHERE INVITE SHOULD LIVE
    def perform_invite(self, serializer):
        reg_location = reverse('register')
        email_addresses = serializer.validated_data.get('emails')
        organization = wfm.Organization.objects.values(
            'organization_uuid', 'name').get(coreuser__user=self.request.user)

        registered_emails = User.objects.filter(email__in=email_addresses)\
            .values_list('email', flat=True)

        for email_address in email_addresses:
            if email_address not in registered_emails:
                # build the invitation link
                invitation_link = self.request.build_absolute_uri(reg_location)
                query_params = {
                    'organization_uuid': organization['organization_uuid'],
                    'email': urlsafe_base64_encode
                    (force_bytes(email_address)).decode()
                }
                qp = urllib.urlencode(query_params)
                invitation_link += '?{}'.format(qp)

                # create the used context for the E-mail templates
                context = {
                    'invitation_link': invitation_link,
                    'org_admin_name': self.request.user.core_user.name,
                    'organization_name': organization['name']
                }
                text_content = loader.render_to_string(
                    'email/coreuser/invitation.txt', context, using=None)
                html_content = loader.render_to_string(
                    'email/coreuser/invitation.html', context, using=None)

                # send the invitation email
                msg = EmailMultiAlternatives(
                    subject='Application Access', # TODO we need to make this dynamic
                    body=text_content,
                    to=[email_address],
                    reply_to=[settings.DEFAULT_REPLY_TO]
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()

    def get_serializer_class(self):
        if self.request and self.request.method == 'POST':
            invitation_path = reverse('coreuser-invite')
            if self.request._request.path == invitation_path:
                return serializers.CoreUserInvitationSerializer

        return serializers.CoreUserSerializer

    def get_permissions(self):
        # different permissions for the invitation process
        if self.request.method == 'POST':
            invitation_path = reverse('coreuser-invite')
            if self.request.path == invitation_path:
                return [AllowOnlyOrgAdmin()]

        return super(CoreUserViewSet, self).get_permissions()

    filter_fields = ('organization__id',)
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

    def list(self, request):
        # Use this queryset or the django-filters lib will not work
        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_superuser:
            organization_id = wfm.CoreUser.objects. \
                values_list('organization_id', flat=True). \
                get(user=request.user)
            queryset = queryset.filter(id=organization_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def subscription(self, request, pk):
        instance = self.get_object()
        try:
            result = Subscription.retrieve(instance.chargebee_subscription_id)
            subscription = result.subscription
            result = Plan.retrieve(subscription.plan_id)
            plan = result.plan
        except Exception as e:
            logger.warn(e)
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
                'used_seats': instance.chargebee_used_seats
            }

            return Response(data, status=status.HTTP_200_OK)

    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (IsOrgMember,)
    queryset = wfm.Organization.objects.all()
    serializer_class = serializers.OrganizationSerializer


class WorkflowLevel2ViewSet(viewsets.ModelViewSet):
    """
    title:
    Workflow Level 2 is the secondary building block for creating relational lists, navigation or generic use case objects
    in the application core.

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

    def list(self, request):
        # Use this queryset or the django-filters lib will not work
        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_superuser:
            organization_id = wfm.CoreUser.objects. \
                values_list('organization_id', flat=True). \
                get(user=request.user)
            if wfm.ROLE_ORGANIZATION_ADMIN in request.user.groups.values_list(
                    'name', flat=True):
                queryset = queryset.filter(
                    workflowlevel1__organization_id=organization_id)
            else:
                wflvl1_ids = wfm.WorkflowTeam.objects.filter(
                    workflow_user__user=request.user).values_list(
                    'workflowlevel1__id', flat=True)
                queryset = queryset.filter(
                    workflowlevel1__organization_id=organization_id,
                    workflowlevel1__in=wflvl1_ids)

        nested = request.GET.get('nested_models')
        if nested is not None and (nested.lower() == 'true' or nested == '1'):
            self.serializer_class = serializers.WorkflowLevel2FullSerializer

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

        nested = request.GET.get('nested_models')
        if nested is not None and (nested.lower() == 'true' or nested == '1'):
            self.serializer_class = serializers.WorkflowLevel2FullSerializer

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    filter_fields = ('level2_uuid',
                     'workflowlevel1__name', 'workflowlevel1__id')
    ordering = ('name',)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,
                       filters.OrderingFilter)
    queryset = wfm.WorkflowLevel2.objects.all()
    permission_classes = (AllowTolaRoles, IsOrgMember)
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

    def list(self, request):
        # Use this queryset or the django-filters lib will not work
        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_superuser:
            user_groups = request.user.groups.values_list('name', flat=True)
            if wfm.ROLE_ORGANIZATION_ADMIN in user_groups:
                organization_id = wfm.CoreUser.objects. \
                    values_list('organization_id', flat=True). \
                    get(user=request.user)
                queryset = queryset.filter(
                    workflowlevel1__organization_id=organization_id)
            else:
                wflvl1_ids = wfm.WorkflowTeam.objects.filter(
                    workflow_user__user=request.user).values_list(
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

    filter_fields = ('language',)
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
    def list(self, request):
        # Use this queryset or the django-filters lib will not work
        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_superuser:
            if wfm.ROLE_ORGANIZATION_ADMIN in request.user.groups.values_list(
                    'name', flat=True):
                organization_id = wfm.CoreUser.objects. \
                    values_list('organization_id', flat=True). \
                    get(user=request.user)
                queryset = queryset.filter(
                    workflow_user__organization_id=organization_id)
            else:
                wflvl1_ids = wfm.WorkflowTeam.objects.filter(
                    workflow_user__user=request.user).values_list(
                    'workflowlevel1__id', flat=True)
                queryset = queryset.filter(workflowlevel1__in=wflvl1_ids)

        nested = request.GET.get('nested_models')
        if nested is not None and (nested.lower() == 'true' or nested == '1'):
            self.serializer_class = serializers.WorkflowTeamListFullSerializer

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    filter_fields = ('workflowlevel1__organization__id',)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (AllowTolaRoles,)
    queryset = wfm.WorkflowTeam.objects.all()
    serializer_class = serializers.WorkflowTeamSerializer


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

    def list(self, request):
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
    A portfolio can be associated with a workflow level 1 or 2 to provide additional organizational structure for a workflow.
    This can be used for example in a project workflow to collect multiple workflows into one folder or grouping or in a navigational
    grouping as a way to provide a secondary site or structure.

    retrieve:
    Return the given portfolio.

    list:
    Return a list of all the existing portfolios.

    create:
    Create a new portfolio instance.
    """

    def list(self, request):
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
        portfolio.organization = request.user.core_user.organization
        portfolio.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    permission_classes = (AllowTolaRoles, IsOrgMember)
    queryset = wfm.Portfolio.objects.all()
    serializer_class = serializers.PortfolioSerializer


"""
GraphQL views from Graphene
"""
from graphene_django.views import GraphQLView
from django.contrib.auth.mixins import LoginRequiredMixin

class DRFAuthenticatedGraphQLView(GraphQLView):
    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super(GraphQLView, cls).as_view(*args, **kwargs)
        return view