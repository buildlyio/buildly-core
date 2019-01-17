import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

import factories

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

    def _create_oauth_application(self):
        if settings.OAUTH_CLIENT_ID is not None:
            self._application = factories.Application(
                id=1,
                name='bifrost',
                client_id=settings.OAUTH_CLIENT_ID,
            )


    @transaction.atomic
    def handle(self, *args, **options):
        self._create_oauth_application()
