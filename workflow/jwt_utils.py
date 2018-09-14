# -*- coding: utf-8 -*-
from workflow.models import CoreUser, ROLE_SUPER_USER


def payload_enricher(request):
    if request.POST.get('username'):
        username = request.POST.get('username')
        is_superuser = CoreUser.objects.values_list(
                'user__is_superuser', flat=True).get(
                user__username=username)
        if is_superuser:
            role = ROLE_SUPER_USER
        else:
            role = CoreUser.objects.values_list(
                'user__groups__name', flat=True).get(
                user__username=username)

        return {
            'user_uuid': CoreUser.objects.values_list(
                'tola_user_uuid', flat=True).get(
                user__username=username),
            'organization_uuid': CoreUser.objects.values_list(
                'organization__organization_uuid', flat=True).get(
                user__username=username),
            'role': role
        }
    else:
        return {}
