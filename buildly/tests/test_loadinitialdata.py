import logging
import sys

from django.conf import settings
from django.core.management import call_command
from django.test import TransactionTestCase, override_settings

from oauth2_provider.models import Application
from core.models import CoreGroup, CoreUser, Organization


class DevNull(object):
    def write(self, data):
        pass


class LoadInitialDataTest(TransactionTestCase):
    def setUp(self):
        # Disable loggers. Do notice that pdb or print won't work neither
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        sys.stdout = DevNull()
        sys.stderr = DevNull()
        logging.disable(logging.ERROR)

    def tearDown(self):
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        logging.disable(logging.NOTSET)

    @override_settings(DEBUG=True)
    @override_settings(OAUTH_CLIENT_ID='123')
    @override_settings(OAUTH_CLIENT_SECRET='456')
    def test_full_initial_data(self):
        args = []
        opts = {}
        call_command('loadinitialdata', *args, **opts)

        assert CoreGroup.objects.filter(name='Global Admin', is_global=True, permissions=15).count() == 1
        assert Organization.objects.filter(name=settings.DEFAULT_ORG).count() == 1
        assert Application.objects.filter(client_id=settings.OAUTH_CLIENT_ID,
                                          client_secret=settings.OAUTH_CLIENT_SECRET).count() == 1
        assert CoreUser.objects.filter(is_superuser=True).count() == 1

    @override_settings(DEBUG=True)
    @override_settings(DEFAULT_ORG='')
    @override_settings(OAUTH_CLIENT_ID='123')
    @override_settings(OAUTH_CLIENT_SECRET='456')
    def test_without_default_organization(self):
        args = []
        opts = {}
        call_command('loadinitialdata', *args, **opts)

        assert CoreGroup.objects.filter(name='Global Admin', is_global=True, permissions=15).count() == 1
        assert Organization.objects.all().count() == 0
        assert Application.objects.filter(client_id=settings.OAUTH_CLIENT_ID,
                                          client_secret=settings.OAUTH_CLIENT_SECRET).count() == 1
        assert CoreUser.objects.filter(is_superuser=True).count() == 1

    @override_settings(DEBUG=True)
    @override_settings(OAUTH_CLIENT_ID='')
    @override_settings(OAUTH_CLIENT_SECRET='')
    def test_without_oauth_credentials(self):
        args = []
        opts = {}
        call_command('loadinitialdata', *args, **opts)

        assert CoreGroup.objects.filter(name='Global Admin', is_global=True, permissions=15).count() == 1
        assert Organization.objects.filter(name=settings.DEFAULT_ORG).count() == 1
        assert Application.objects.all().count() == 0
        assert CoreUser.objects.filter(is_superuser=True).count() == 1

    @override_settings(DEBUG=True)
    @override_settings(OAUTH_CLIENT_ID='123')
    @override_settings(OAUTH_CLIENT_SECRET='456')
    def test_create_user_debug_no_password(self):
        args = []
        opts = {}
        call_command('loadinitialdata', *args, **opts)

        assert CoreGroup.objects.filter(name='Global Admin', is_global=True, permissions=15).count() == 1
        assert Organization.objects.filter(name=settings.DEFAULT_ORG).count() == 1
        assert Application.objects.filter(client_id=settings.OAUTH_CLIENT_ID,
                                          client_secret=settings.OAUTH_CLIENT_SECRET).count() == 1
        assert CoreUser.objects.filter(is_superuser=True).count() == 1

    @override_settings(DEBUG=False)
    @override_settings(OAUTH_CLIENT_ID='123')
    @override_settings(OAUTH_CLIENT_SECRET='456')
    def test_create_user_no_debug_no_password(self):
        args = []
        opts = {}
        call_command('loadinitialdata', *args, **opts)

        assert CoreGroup.objects.filter(name='Global Admin', is_global=True, permissions=15).count() == 1
        assert Organization.objects.filter(name=settings.DEFAULT_ORG).count() == 1
        assert Application.objects.filter(client_id=settings.OAUTH_CLIENT_ID,
                                          client_secret=settings.OAUTH_CLIENT_SECRET).count() == 1
        assert CoreUser.objects.filter(is_superuser=True).count() == 0
