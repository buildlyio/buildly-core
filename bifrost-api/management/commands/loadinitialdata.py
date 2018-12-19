# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from oauth2_provider.models import Application

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
    Loads initial data for Bifrost.
    """

    def _create_oauth_application(self):
        application = None

        if settings.OAUTH_CLIENT_ID is not None:
            application = Application.objects.get_or_create(
                name='bifrost',
                client_id=settings.OAUTH_CLIENT_ID,
                client_type=Application.CLIENT_PUBLIC,
                authorization_grant_type=Application.GRANT_PASSWORD,
                skip_authorization=True,
            )

        return application

    @transaction.atomic
    def handle(self, *args, **options):
        self._create_oauth_application()
