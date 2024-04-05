import logging

from rest_framework import permissions

from core.models import Organization


logger = logging.getLogger(__name__)


def merge_permissions(permissions1: str, permissions2: str) -> str:
    """ Merge two CRUD permissions string representations"""
    return ''.join(
        map(str, [max(int(i), int(j)) for i, j in zip(permissions1, permissions2)])
    )


def has_permission(permissions_: str, method: str) -> bool:
    """ Check if HTTP method or CRUD action corresponds to permissions"""
    methods = {
        # HTTP methods
        'POST': 0,
        'GET': 1,
        'HEAD': 1,
        'PUT': 2,
        'PATCH': 2,
        'DELETE': 3,
        'OPTIONS': 1,
        # CRUD actions
        'create': 0,
        'list': 1,
        'retrieve': 1,
        'update': 2,
        'partial_update': 2,
        'destroy': 3,
    }
    try:
        i = methods[method]
    except KeyError:
        logger.warning(f'No view method with such name: {method}')
        return False
    return bool(int(permissions_[i]))


class IsSuperUserBrowseableAPI(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if view.__class__.__name__ == 'SchemaView':
                return request.user.is_superuser
            else:
                return True
        return False


class IsSuperUser(permissions.BasePermission):
    """
    Only superusers are allowed to access.
    """

    def has_permission(self, request, view):
        return request.user.is_active and request.user.is_superuser


class AllowAuthenticatedRead(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            if request.user.is_anonymous:
                return False
        return True


class AllowOnlyOrgAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        if request.user.is_active and request.user.is_global_admin:
            return True

        if request.user.is_org_admin:
            return True

        return False


class IsOrgMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous or not request.user.is_active:
            return False

        if request.user.is_superuser or request.user.is_global_admin:
            return True

        if view.action == 'create':
            user_org = request.user.organization_id

            if 'organization' in request.data:
                org_serializer = view.get_serializer_class()().get_fields()[
                    'organization'
                ]
                primitive_value = request.data.get('organization')
                org = org_serializer.run_validation(primitive_value)
                return org.pk == user_org
            elif 'CoreGroup' in view.__class__.__name__:
                return False

        return True

    def has_object_permission(self, request, view, obj):
        """
        Object level permissions are used to determine if a user
        should be allowed to act on a particular object
        """

        if request.user.is_active and request.user.is_global_admin:
            return True
        user_org = request.user.organization_id
        try:
            if obj.__class__ in [Organization]:
                return obj.pk == user_org
            elif hasattr(obj, 'organization'):
                return obj.organization.pk == user_org
        except AttributeError:
            pass
        return False
