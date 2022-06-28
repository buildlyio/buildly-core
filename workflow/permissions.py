import logging
from collections import defaultdict

from rest_framework import permissions
from rest_framework.relations import ManyRelatedField
from django.http import QueryDict

from core.models import PERMISSIONS_VIEW_ONLY
from core.permissions import merge_permissions, has_permission
from workflow.models import WorkflowLevel1, WorkflowLevel2


logger = logging.getLogger(__name__)


class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    The request is authenticated as a superuser, or is a read-only request.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user
            and request.user.is_authenticated
            and request.user.is_superuser
        )


class CoreGroupsPermissions(permissions.BasePermission):
    def _get_workflowlevel(self, view, request_data, field_name):
        wflvl_serializer = view.serializer_class().get_fields()[field_name]

        # Check if the field is Many-To-Many or not
        if wflvl_serializer.__class__ == ManyRelatedField and isinstance(
            request_data, QueryDict
        ):
            primitive_value = request_data.getlist(field_name)
        else:
            primitive_value = request_data.get(field_name)

        # Get objects using their URLs
        return wflvl_serializer.run_validation(primitive_value)

    def _get_workflowlevel1_from_level2(self, workflowlevel2_uuid):
        try:
            workflowlevel2 = WorkflowLevel2.objects.get(level2_uuid=workflowlevel2_uuid)
        except WorkflowLevel2.DoesNotExist:
            return None
        else:
            return workflowlevel2.workflowlevel1

    def has_permission(self, request, view):
        if request.user.is_anonymous or not request.user.is_active:
            return False

        if request.user.is_global_admin:
            return True

        # TODO: check if we can optimize following query using 'through' M2M Models
        user_groups = request.user.core_groups.prefetch_related(
            'workflowlevel1s', 'workflowlevel2s'
        )

        # sort up permissions into more convenient way (default is read-only '0100')
        viewonly_display_permissions = '{0:04b}'.format(PERMISSIONS_VIEW_ONLY)
        global_permissions, org_permissions = (
            viewonly_display_permissions,
            viewonly_display_permissions,
        )
        wl1_permissions = defaultdict(lambda: viewonly_display_permissions)
        wl2_permissions = defaultdict(lambda: viewonly_display_permissions)
        for group in user_groups:
            if group.is_global:
                global_permissions = merge_permissions(
                    global_permissions, group.display_permissions
                )
            elif group.is_org_level:
                org_permissions = merge_permissions(
                    org_permissions, group.display_permissions
                )
            else:
                for wl1 in group.workflowlevel1s.all():
                    wl1_permissions[wl1.pk] = merge_permissions(
                        wl1_permissions[wl1.pk], group.display_permissions
                    )
                for wl2 in group.workflowlevel2s.all():
                    wl2_permissions[wl2.pk] = merge_permissions(
                        wl2_permissions[wl2.pk], group.display_permissions
                    )

        action = view.action
        if has_permission(global_permissions, action):
            return True

        if has_permission(org_permissions, action):
            return True

        if action in 'create':
            data = request.data

            # Check WorkflowLevel1 permissions
            if data.get('workflowlevel1') or data.get('workflowlevel2'):
                if data.get('workflowlevel1'):
                    wflvl1 = self._get_workflowlevel(view, data, 'workflowlevel1')
                else:
                    wflvl1 = self._get_workflowlevel1_from_level2(
                        data['workflowlevel2']
                    )

                if not wflvl1:
                    return False
                elif not isinstance(wflvl1, list):
                    wflvl1 = [wflvl1]

                for item in wflvl1:
                    if has_permission(wl1_permissions[item.pk], action):
                        return True

                # TODO: Check WorkflowLevel2 permissions

            return False

        # Otherwise check object permissions
        return True

    def _queryset(self, view):
        """
        Return the queryset of the view
        :param view:
        :return: QuerySet
        """
        assert (
            hasattr(view, 'get_queryset') or getattr(view, 'queryset', None) is not None
        ), (
            'Cannot apply {} on a view that does not set '
            '`.queryset` or have a `.get_queryset()` method.'
        ).format(
            self.__class__.__name__
        )

        if hasattr(view, 'get_queryset'):
            queryset = view.get_queryset()
            assert queryset is not None, '{}.get_queryset() returned None'.format(
                view.__class__.__name__
            )
            return queryset

        return view.queryset

    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous or not request.user.is_active:
            return False

        # TODO: Need some optimization pre-fetching all user's core gropus
        if request.user.is_global_admin:
            return True

        queryset = self._queryset(view)
        model_cls = queryset.model

        if request.user.is_org_admin:
            return True

        if model_cls is WorkflowLevel1:
            # Permissions on WorkflowLevel1 itself are defined by Org-level permissions
            groups = request.user.core_groups.filter(is_org_level=True)
        elif hasattr(obj, 'workflowlevel1'):
            groups = request.user.core_groups.all().intersection(
                obj.workflowlevel1.core_groups.all()
            )
        else:
            return True

        if hasattr(view, 'action'):
            for group in groups:
                if has_permission(group.display_permissions, view.action):
                    return True

        return False
