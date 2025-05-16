import logging
import datetime

import jwt
from django.conf import settings

from core.models import CoreUser, Organization
from gateway.exceptions import PermissionDenied

logger = logging.getLogger(__name__)

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# New SimpleJWT serializer
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['core_user_uuid'] = str(user.core_user_uuid)
        token['username'] = user.username
        if user.organization:
            token['organization_uuid'] = str(user.organization.organization_uuid)
        else:
            token['organization_uuid'] = None
        return token


# old payload not in use
def payload_enricher(request):
    if request.POST.get('username'):
        username = request.POST.get('username')
        try:
            user = CoreUser.objects.values(
                'core_user_uuid', 'organization__organization_uuid'
            ).get(username=username)
        except CoreUser.DoesNotExist:
            logger.error('No matching CoreUser found.')
            raise PermissionDenied('No matching CoreUser found.')
        return {
            'core_user_uuid': user['core_user_uuid'],
            'organization_uuid': str(user['organization__organization_uuid']),
        }
    return {}


def create_invitation_token(email_address: str, organization: Organization):
    exp_hours = datetime.timedelta(hours=settings.INVITATION_EXPIRE_HOURS)
    payload = {
        'email': email_address,
        'org_uuid': str(organization.organization_uuid) if organization else None,
        'exp': datetime.datetime.utcnow() + exp_hours,
    }
    return jwt.encode(payload, settings.TOKEN_SECRET_KEY, algorithm='HS256').decode('utf-8')
