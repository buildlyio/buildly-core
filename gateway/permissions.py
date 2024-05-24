import logging

from django.db.models import Q
from rest_framework import permissions

from core.models import LogicModule, PERMISSIONS_NO_ACCESS
from core.permissions import merge_permissions, has_permission

from gateway.exceptions import ServiceDoesNotExist

logger = logging.getLogger(__name__)


class AllowLogicModuleGroup(permissions.BasePermission):
    @staticmethod
    def _get_logic_module(service_name: str) -> LogicModule:
        try:
            return LogicModule.objects.prefetch_related('core_groups').get(
                endpoint_name=service_name
            )
        except LogicModule.DoesNotExist:
            raise ServiceDoesNotExist(f'Service "{service_name}" not found.')

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        if request.user.is_superuser:
            return True

        service_name = view.kwargs['service']
        logic_module = self._get_logic_module(service_name=service_name)
        logic_module_group = logic_module.core_groups.filter(
            Q(is_global=True)
            | Q(
                organization=request.user.organization,
                is_global=False,
                is_org_level=True,
            )
        )

        if logic_module_group:
            # default permission is no access '0000'
            viewonly_display_permissions = '{0:04b}'.format(PERMISSIONS_NO_ACCESS)
            global_permissions, org_permissions = (
                viewonly_display_permissions,
                viewonly_display_permissions,
            )
            for group in logic_module_group:
                if group.is_global:
                    global_permissions = merge_permissions(
                        global_permissions, group.display_permissions
                    )
                elif group.is_org_level:
                    org_permissions = merge_permissions(
                        org_permissions, group.display_permissions
                    )

            method = request.META['REQUEST_METHOD']
            if has_permission(global_permissions, method):
                return True

            if has_permission(org_permissions, method):
                return True

            return False
        else:
            return True
