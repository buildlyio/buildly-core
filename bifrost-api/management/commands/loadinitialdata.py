import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction

from oauth2_provider.models import Application

import factories
from workflow.models import (ROLE_VIEW_ONLY, ROLE_ORGANIZATION_ADMIN,
                             ROLE_PROGRAM_ADMIN, ROLE_PROGRAM_TEAM)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
    Loads initial data for Bifrost.
    """

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        # Note: for the lists we fill the first element with an empty value for
        # development readability (id == position).
        self._applications = []
        self._groups = ['']
        self._user = None

    def _create_oauth_application(self):
        if settings.OAUTH2_CLIENT_ID and settings.OAUTH2_CLIENT_SECRET:
            app = Application.objects.get_or_create(
                name='bifrost oauth2',
                client_id=settings.OAUTH2_CLIENT_ID,
                client_secret=settings.OAUTH2_CLIENT_SECRET,
                client_type=Application.CLIENT_PUBLIC,
                authorization_grant_type=Application.GRANT_PASSWORD
            )
            self._applications.append(app)

        if (settings.SOCIAL_AUTH_CLIENT_ID and
                settings.SOCIAL_AUTH_CLIENT_SECRET):
            app = Application.objects.get_or_create(
                name='bifrost social auth',
                redirect_uris=settings.SOCIAL_AUTH_LOGIN_REDIRECT_URL,
                client_id=settings.SOCIAL_AUTH_CLIENT_ID,
                client_secret=settings.SOCIAL_AUTH_CLIENT_SECRET,
                client_type=Application.CLIENT_CONFIDENTIAL,
                authorization_grant_type=Application.GRANT_CLIENT_CREDENTIALS
            )
            self._applications.append(app)

    def _create_groups(self):
        self._groups.append(factories.Group(
            id=1,
            name=ROLE_VIEW_ONLY,
        ))

        self._groups.append(factories.Group(
            id=2,
            name=ROLE_ORGANIZATION_ADMIN,
        ))

        self._groups.append(factories.Group(
            id=3,
            name=ROLE_PROGRAM_ADMIN,
        ))

        self._groups.append(factories.Group(
            id=4,
            name=ROLE_PROGRAM_TEAM,
        ))

    def _create_user(self):
        User.objects.filter(username='admin').delete()
        user = User.objects.create_superuser(
            first_name='System',
            last_name='Admin',
            username='admin',
            email='admin@example.com',
            password='ttmtola1977'
        )
        self._core_user = factories.CoreUser(user=user)

    @transaction.atomic
    def handle(self, *args, **options):
        self._create_groups()
        self._create_oauth_application()
        self._create_user()
