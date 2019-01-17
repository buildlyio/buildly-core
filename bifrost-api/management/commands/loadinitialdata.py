import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

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
        self._application = None
        self._groups = ['']

    def _create_oauth_application(self):
        if settings.OAUTH_CLIENT_ID is not None:
            self._application = factories.Application(
                id=1,
                name='bifrost',
                client_id=settings.OAUTH_CLIENT_ID,
            )

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

    @transaction.atomic
    def handle(self, *args, **options):
        self._create_groups()
        self._create_oauth_application()
