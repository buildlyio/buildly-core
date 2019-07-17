from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError

from gateway.utils import valid_uuid4


class OrganizationPermission(IsAuthenticated):

    def has_permission(self, request, view):
        """Check if the organization_uuid in the JWT-Header is valid."""
        if super().has_permission(request, view) and \
                getattr(request, 'session', None) and \
                request.session.get('jwt_organization_uuid'):
            organization_uuid = request.session['jwt_organization_uuid']
            if not valid_uuid4(organization_uuid):
                raise ValidationError(
                    f'organization_uuid from JWT Token "{organization_uuid}" is not a valid UUID.'
                )
            return True
        return False

    def has_object_permission(self, request, _view, obj):
        if getattr(request, 'session', None):
            if request.session.get('jwt_organization_uuid') == \
                    str(obj.organization.organization_uuid):
                return True
            else:
                raise PermissionDenied('User is not in the same organization '
                                       'as the object.')
