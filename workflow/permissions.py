from rest_framework import permissions
from rest_framework.relations import ManyRelatedField

from django.http import QueryDict

from workflow.models import (
    ROLE_ORGANIZATION_ADMIN, ROLE_VIEW_ONLY, ROLE_PROGRAM_ADMIN,
    ROLE_PROGRAM_TEAM, WorkflowTeam, Organization, Milestone,
    Portfolio, WorkflowLevel1, WorkflowLevel2, WorkflowLevel2Sort,CoreUser)

PERMISSIONS_ORG_ADMIN = {
    'create': True,
    'edit': True,
    'remove': True,
    'manageUsers': True,
    'view': True,
}

PERMISSIONS_ADMIN = PERMISSIONS_ORG_ADMIN

PERMISSIONS_PROGRAM_ADMIN = PERMISSIONS_ORG_ADMIN

PERMISSIONS_PROGRAM_TEAM = {
    'create': True,
    'edit': True,
    'remove': False,
    'manageUsers': False,
    'view': True,
}

PERMISSIONS_VIEW_ONLY = {
    'create': False,
    'edit': False,
    'remove': False,
    'manageUsers': False,
    'view': True,
}


class IsSuperUserBrowseableAPI(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if view.__class__.__name__ == 'SchemaView':
                return request.user.is_superuser
            else:
                return True
        return False


class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    The request is authenticated as a superuser, or is a read-only request.
    """

    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS or
                request.user and
                request.user.is_authenticated and
                request.user.is_superuser
        )


class AllowAuthenticatedRead(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            if request.user.is_anonymous:
                return False
            if not (request.user and request.user.is_authenticated):
                return False
        return True


class AllowOnlyOrgAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous and not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        user_groups = request.user.groups.values_list('name', flat=True)
        if ROLE_ORGANIZATION_ADMIN in user_groups:
            return True

        return False


class IsOrgMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        if request.user.is_superuser:
            return True

        if view.action == 'create':
            user_org = CoreUser.objects.values_list(
                'organization_id', flat=True).get(user=request.user)

            if 'organization' in request.data:
                org_serializer = view.get_serializer_class()().get_fields()[
                    'organization']
                primitive_value = request.data.get('organization')
                org = org_serializer.run_validation(primitive_value)
                return org.id == user_org
            if 'indicator' in request.data:
                indicator_serializer = view.serializer_class().get_fields()[
                    'indicator']
                primitive_value = request.data.get('indicator')
                indicator = indicator_serializer.run_validation(
                    primitive_value)
                return indicator.workflowlevel1.filter(
                    organization_id=user_org).exists()

        return True

    def has_object_permission(self, request, view, obj):
        """
        Object level permissions are used to determine if a user
        should be allowed to act on a particular object
        """

        if request.user.is_superuser:
            return True
        user_groups = request.user.groups.values_list('name', flat=True)
        org_admin = True if ROLE_ORGANIZATION_ADMIN in user_groups else False
        user_org = CoreUser.objects.values_list(
            'organization_id', flat=True).get(user=request.user)
        try:
            if obj.__class__ in [Milestone,
                                 Portfolio, WorkflowLevel1]:
                return obj.organization.id == user_org
            elif obj.__class__ in [WorkflowLevel2,
                                   WorkflowLevel2Sort]:
                return obj.__class__.objects.filter(
                    workflowlevel1__organization=user_org, id=obj.id).exists()
            elif obj.__class__ in [Organization]:
                return obj.id == user_org
            elif obj.__class__ in [WorkflowTeam]:
                if org_admin:
                    return obj.__class__.objects.filter(
                        workflow_user__organization=user_org,
                        id=obj.id).exists()
                else:
                    return obj.__class__.objects.filter(
                        workflowlevel1__organization=user_org,
                        id=obj.id).exists()
        except AttributeError:
            pass
        return False


class AllowTolaRoles(permissions.BasePermission):
    def _get_workflowlevel1(self, view, request_data):
        wflvl1_serializer = view.serializer_class().get_fields()[
            'workflowlevel1']

        # Check if the field is Many-To-Many or not
        if wflvl1_serializer.__class__ == ManyRelatedField and \
                isinstance(request_data, QueryDict):
            primitive_value = request_data.getlist('workflowlevel1')
        else:
            primitive_value = request_data.get('workflowlevel1')

        # Get objects using their URLs
        return wflvl1_serializer.run_validation(primitive_value)

    def _get_workflowlevel1_from_level2(self, workflowlevel2_uuid):
        try:
            workflowlevel2 = WorkflowLevel2.objects.get(
                level2_uuid=workflowlevel2_uuid)
        except WorkflowLevel2.DoesNotExist:
            return None
        else:
            return workflowlevel2.workflowlevel1

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        if request.user.is_superuser:
            return True

        user_groups = request.user.groups.values_list('name', flat=True)

        queryset = self._queryset(view)
        model_cls = queryset.model
        if view.action == 'create':
            user_org = request.user.core_user.organization
            data = request.data

            if data.get('workflowlevel1') or data.get('workflowlevel2_uuid'):
                if data.get('workflowlevel1'):
                    wflvl1 = self._get_workflowlevel1(view, data)
                elif data.get('workflowlevel2_uuid'):
                    wflvl1 = self._get_workflowlevel1_from_level2(
                        data['workflowlevel2_uuid'])

                if not wflvl1:
                    return False
                # We use a list to fetch the program teams
                elif not isinstance(wflvl1, list):
                    wflvl1 = [wflvl1]

                team_groups = WorkflowTeam.objects.filter(
                    workflow_user=request.user.core_user,
                    workflowlevel1__in=wflvl1).values_list(
                    'role__name', flat=True)

                if model_cls in [WorkflowLevel2]:
                    if (ROLE_ORGANIZATION_ADMIN in user_groups or
                            ROLE_PROGRAM_ADMIN in team_groups or
                            ROLE_PROGRAM_TEAM in team_groups):
                        is_allowed_role = True
                    else:
                        is_allowed_role = False
                    is_same_org = all(x.organization == user_org
                                      for x in wflvl1)
                    return is_allowed_role and is_same_org
                elif model_cls is WorkflowTeam:
                    return (((ROLE_VIEW_ONLY not in team_groups and
                            ROLE_PROGRAM_TEAM not in team_groups) or
                             ROLE_ORGANIZATION_ADMIN in user_groups) and
                            all(x.organization == user_org for x in wflvl1))

            elif model_cls is Portfolio:
                return ROLE_ORGANIZATION_ADMIN in user_groups

        return True

    def _queryset(self, view):
        """
        Return the queryset of the view
        :param view:
        :return: QuerySet
        """
        assert hasattr(view, 'get_queryset') \
            or getattr(view, 'queryset', None) is not None, (
            'Cannot apply {} on a view that does not set '
            '`.queryset` or have a `.get_queryset()` method.'
        ).format(self.__class__.__name__)

        if hasattr(view, 'get_queryset'):
            queryset = view.get_queryset()
            assert queryset is not None, (
                '{}.get_queryset() returned None'.format(
                    view.__class__.__name__)
            )
            return queryset
        return view.queryset

    def has_object_permission(self, request, view, obj):
        """
        Object level permissions are used to determine if a user
        should be allowed to act on a particular object
        """
        if request.user and request.user.is_authenticated:
            if request.user.is_superuser:
                return True

            queryset = self._queryset(view)
            model_cls = queryset.model

            user_groups = request.user.groups.values_list('name', flat=True)
            if ROLE_ORGANIZATION_ADMIN in user_groups:
                return True

            if model_cls is Portfolio:
                team_groups = WorkflowTeam.objects.filter(
                    workflow_user=request.user.core_user,
                    workflowlevel1__portfolio=obj).values_list(
                    'role__name', flat=True)
                if ROLE_PROGRAM_ADMIN in team_groups or ROLE_PROGRAM_TEAM in \
                        team_groups:
                    return view.action == 'retrieve'
            elif model_cls is WorkflowTeam:
                team_groups = WorkflowTeam.objects.filter(
                    workflow_user=request.user.core_user,
                    workflowlevel1=obj.workflowlevel1).values_list(
                    'role__name', flat=True)
                if ROLE_PROGRAM_ADMIN in team_groups:
                    return True
                else:
                    return view.action == 'retrieve'
            elif model_cls is WorkflowLevel1:
                team_groups = WorkflowTeam.objects.filter(
                    workflow_user=request.user.core_user,
                    workflowlevel1=obj).values_list(
                    'role__name', flat=True)
                if ROLE_PROGRAM_ADMIN in team_groups:
                    return True
                elif ROLE_PROGRAM_TEAM in team_groups:
                    return view.action != 'destroy'

            elif model_cls in [WorkflowLevel2]:
                workflowlevel1 = obj.workflowlevel1
                team_groups = WorkflowTeam.objects.filter(
                    workflow_user=request.user.core_user,
                    workflowlevel1=workflowlevel1).values_list(
                    'role__name', flat=True)
                if ROLE_PROGRAM_ADMIN in team_groups:
                    return True
                elif ROLE_VIEW_ONLY in team_groups:
                    return view.action == 'retrieve'
            else:
                return True

        return False
