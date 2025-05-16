import logging

from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import Group
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import ROLE_VIEW_ONLY, ROLE_ORGANIZATION_ADMIN, ROLE_WORKFLOW_ADMIN, ROLE_WORKFLOW_TEAM, \
    Organization, CoreUser, CoreGroup, OrganizationType


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
    Loads initial data for Buildly.
    """

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        # Note: for the lists we fill the first element with an empty value for
        # development readability (id == position).
        self._application = None
        self._groups = ['']
        self._user = None
        self._su_group = None
        self._default_org = None

    def _create_organization_types(self):
        if settings.ORGANIZATION_TYPES:
            for organization_type in settings.ORGANIZATION_TYPES:
                OrganizationType.objects.get_or_create(name=organization_type)

    def _create_default_organization(self):
        if settings.DEFAULT_ORG:
            self._default_org, _ = Organization.objects.get_or_create(name=settings.DEFAULT_ORG.lower())

    def _create_groups(self):
        self._su_group = CoreGroup.objects.filter(
            is_global=True, permissions=15
        ).first()
        if not self._su_group:
            logger.info("Creating global CoreGroup")
            self._su_group = CoreGroup.objects.create(
                name='Global Admin', is_global=True, permissions=15
            )

        # TODO: remove this after full Group -> CoreGroup refactoring
        self._groups.append(Group.objects.get_or_create(name=ROLE_VIEW_ONLY))

        self._groups.append(Group.objects.get_or_create(name=ROLE_ORGANIZATION_ADMIN))

        self._groups.append(Group.objects.get_or_create(name=ROLE_WORKFLOW_ADMIN))

        self._groups.append(Group.objects.get_or_create(name=ROLE_WORKFLOW_TEAM))

    def _create_user(self):
        if not CoreUser.objects.filter(is_superuser=True).exists():
            logger.info("Creating Super User")
            user_password = None
            if settings.DEBUG:
                user_password = settings.SUPER_USER_PASSWORD if settings.SUPER_USER_PASSWORD else 'Djf0KG0YDr8m'
            elif settings.SUPER_USER_PASSWORD:
                user_password = settings.SUPER_USER_PASSWORD
            else:
                warning_msg = 'A password for the super user needs to be provided, otherwise, it is not created.'
                logger.warning(warning_msg)
                self.stdout.write(f'{warning_msg}')

            if user_password is not None:
                su = CoreUser.objects.create_superuser(
                    first_name='System',
                    last_name='Admin',
                    username='DA05L19J52XX',
                    email='admin@example.com',
                    password=user_password,
                    organization=self._default_org,
                )
                su.core_groups.add(self._su_group)

    @transaction.atomic
    def handle(self, *args, **options):
        self._create_groups()
        self._create_organization_types()
        self._create_default_organization()
        self._create_user()
        # self._create_oauth_application()
