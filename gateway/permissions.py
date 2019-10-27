import logging

from django.db.models import Q
from rest_framework import permissions

from . exceptions import ServiceDoesNotExist
from . models import LogicModule

from workflow.models import PERMISSIONS_NO_ACCESS


logger = logging.getLogger(__name__)


def merge_permissions(permissions1: str, permissions2: str) -> str:
    """ Merge two CRUD permissions string representations"""
    return ''.join(map(str, [max(int(i), int(j)) for i, j in zip(permissions1, permissions2)]))


def has_permission(permissions_: str, method: str) -> bool:
    """ Check if HTTP method corresponds to permissions"""
    methods = {
        'POST': 0,
        'GET': 1,
        'HEAD': 1,
        'PUT': 2,
        'PATCH': 2,
        'DELETE': 3
    }
    try:
        i = methods[method]
    except KeyError:
        logger.warning(f'No view method with such name: {method}')
        return False
    return bool(int(permissions_[i]))


class AllowLogicModuleGroup(permissions.BasePermission):
    @staticmethod
    def _get_logic_module(service_name: str) -> LogicModule:
        try:
            return LogicModule.objects.prefetch_related('core_groups').get(endpoint_name=service_name)
        except LogicModule.DoesNotExist:
            raise ServiceDoesNotExist(f'Service "{service_name}" not found.')

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        if request.user.is_superuser:
            return True

        service_name = view.kwargs['service']
        logic_module = self._get_logic_module(service_name=service_name)
        logic_module_group = logic_module.core_groups.filter(Q(is_global=True) |
                                                             Q(organization=request.user.organization,
                                                               is_global=False, is_org_level=True))

        if logic_module_group:
            # default permission is no access '0000'
            viewonly_display_permissions = '{0:04b}'.format(PERMISSIONS_NO_ACCESS)
            global_permissions, org_permissions = viewonly_display_permissions, viewonly_display_permissions
            for group in logic_module_group:
                if group.is_global:
                    global_permissions = merge_permissions(global_permissions, group.display_permissions)
                elif group.is_org_level:
                    org_permissions = merge_permissions(org_permissions, group.display_permissions)

            method = request.META['REQUEST_METHOD']
            if has_permission(global_permissions, method):
                return True

            if has_permission(org_permissions, method):
                return True

            return False
        else:
            return True
