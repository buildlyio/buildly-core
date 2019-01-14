# -*- coding: utf-8 -*-
from workflow.models import CoreUser


def payload_enricher(request):
    if request.POST.get('username'):
        username = request.POST.get('username')
        return {
            'user_uuid': CoreUser.objects.values_list(
                'core_user_uuid', flat=True).get(
                user__username=username),
            'organization_uuid': CoreUser.objects.values_list(
                'organization__organization_uuid', flat=True).get(
                user__username=username),
        }
    else:
        return {}
