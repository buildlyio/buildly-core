import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from oauth2_provider.models import Application

import factories
from workflow.models import (
    ROLE_VIEW_ONLY, ROLE_ORGANIZATION_ADMIN,
    ROLE_WORKFLOW_ADMIN, ROLE_WORKFLOW_TEAM, Organization, CoreUser, CoreGroup)

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
        self._su_group = None
        self._default_org = None

    def _create_oauth_application(self):
        if settings.OAUTH_CLIENT_ID and settings.OAUTH_CLIENT_SECRET:
            app, created = Application.objects.update_or_create(
                client_id=settings.OAUTH_CLIENT_ID,
                client_secret=settings.OAUTH_CLIENT_SECRET,
                defaults={
                    'name': 'bifrost oauth2',
                    'client_type': Application.CLIENT_PUBLIC,
                    'authorization_grant_type': Application.GRANT_PASSWORD,
                }
            )
            self._applications.append(app)

        if settings.SOCIAL_AUTH_CLIENT_ID and settings.SOCIAL_AUTH_CLIENT_SECRET:
            urls = list()
            for url in settings.SOCIAL_AUTH_LOGIN_REDIRECT_URLS.values():
                if url:
                    urls.append(url)

            social_auth_redirect_urls = '\n'.join(urls)
            app, created = Application.objects.update_or_create(
                client_id=settings.SOCIAL_AUTH_CLIENT_ID,
                client_secret=settings.SOCIAL_AUTH_CLIENT_SECRET,
                defaults={
                    'name': 'bifrost social auth',
                    'client_type': Application.CLIENT_CONFIDENTIAL,
                    'redirect_uris': social_auth_redirect_urls,
                    'authorization_grant_type': Application.GRANT_CLIENT_CREDENTIALS,
                }
            )
            self._applications.append(app)

    def _create_default_organization(self):
        if settings.DEFAULT_ORG:
            self._default_org, _ = Organization.objects.get_or_create(name=settings.DEFAULT_ORG)

    def _create_groups(self):
        CoreGroup.objects.filter(is_global=True).delete()
        self._su_group = factories.CoreGroup(name='Global Admin', is_global=True, permissions=15)

        # TODO: remove this after full Group -> CoreGroup refactoring
        self._groups.append(factories.Group(
            name=ROLE_VIEW_ONLY,
        ))

        self._groups.append(factories.Group(
            name=ROLE_ORGANIZATION_ADMIN,
        ))

        self._groups.append(factories.Group(
            name=ROLE_WORKFLOW_ADMIN,
        ))

        self._groups.append(factories.Group(
            name=ROLE_WORKFLOW_TEAM,
        ))

    def _create_user(self):
        CoreUser.objects.filter(username='admin').delete()
        su = CoreUser.objects.create_superuser(
            first_name='System',
            last_name='Admin',
            username='admin',
            email='admin@example.com',
            password='ttmtola1977',
            organization=self._default_org,
        )
        su.core_groups.add(self._su_group)

    @transaction.atomic
    def handle(self, *args, **options):
        self._create_groups()
        self._create_default_organization()
        self._create_oauth_application()
        self._create_user()
