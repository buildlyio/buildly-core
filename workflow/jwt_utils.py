from workflow.models import CoreUser
from gateway.exceptions import PermissionDenied


def payload_enricher(request):
    if request.POST.get('username'):
        username = request.POST.get('username')
        try:
            user = CoreUser.objects.values(
                'core_user_uuid', 'organization__organization_uuid').get(
                user__username=username)
        except CoreUser.DoesNotExist:
            raise PermissionDenied('No matching CoreUser found.')
        return {
            'user_uuid': user['core_user_uuid'],
            'organization_uuid': user['organization__organization_uuid'],
        }
    else:
        return {}
