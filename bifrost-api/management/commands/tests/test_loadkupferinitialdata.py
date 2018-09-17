# -*- coding: utf-8 -*-
import datetime
import logging
import sys

from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.management import call_command
from django.db import connection
from django.test import TransactionTestCase, override_settings
import factories
from workflow.models import (
    ROLE_VIEW_ONLY, ROLE_ORGANIZATION_ADMIN, ROLE_PROGRAM_ADMIN,
    ROLE_PROGRAM_TEAM, Organization, CoreUser, WorkflowLevel1, WorkflowLevel2,
    CoreUser,)


class DevNull(object):
    def write(self, data):
        pass


class LoadKupferInitialDataTest(TransactionTestCase):
    def setUp(self):
        settings.CREATE_DEFAULT_PROGRAM = True
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

    @override_settings(DEFAULT_ORG='')
    def test_without_default_organization_conf_var(self):
        args = []
        opts = {}
        with self.assertRaises(ImproperlyConfigured):
            call_command('loadkupferinitialdata', *args, **opts)

    @override_settings(CREATE_DEFAULT_PROGRAM=False)
    def test_without_create_default_program_conf_var(self):
        args = []
        opts = {}
        with self.assertRaises(ImproperlyConfigured):
            call_command('loadkupferinitialdata', *args, **opts)

    def _check_basic_data(self):
        Organization.objects.get(name=settings.DEFAULT_ORG)

        for role_name in (ROLE_VIEW_ONLY, ROLE_ORGANIZATION_ADMIN,
                          ROLE_PROGRAM_ADMIN, ROLE_PROGRAM_TEAM):
            Group.objects.get(name=role_name)

        CoreUser.objects.get(name=settings.DEFAULT_ORG)

        WorkflowLevel1.objects.get(name='Default Program')

    def test_load_basic_data(self):
        args = []
        opts = {}
        call_command('loadkupferinitialdata', *args, **opts)
        self._check_basic_data()

    def test_load_basic_data_two_times_no_crash(self):
        args = []
        opts = {}
        call_command('loadkupferinitialdata', *args, **opts)
        call_command('loadkupferinitialdata', *args, **opts)
        self._check_basic_data()

    def test_load_demo_data_check_indices_reset(self):
        """
        We add new data to see if there is a primary key collission and
        then we check which will be the next ID.
        """
        args = []
        opts = {}
        call_command('loadkupferinitialdata', *args, **opts)

        Group.objects.create(name='Some role')

        cursor = connection.cursor()
        cursor.execute("SELECT nextval('auth_group_id_seq')")
        pos = int(cursor.fetchone()[0])
        self.assertEqual(pos, 6, pos)

    def _check_demo_data(self):
        self.assertEqual(Contact.objects.count(), 20)
        contact = Contact.objects.get(pk=20)
        self.assertEqual(contact.first_name, 'Petra')
        self.assertEqual(contact.last_name, 'Zimmermann')
        self.assertEqual(contact.phones,
                         [{'type': 'mobile', 'number': '+491649808408'}])
        self.assertEqual(contact.addresses,
                         [{
                             'type': 'home',
                             'city': 'Hannover',
                             'house_number': '48',
                             'country': 'Germany',
                             'street': 'Finkenweg',
                             'postal_code': '30159',
                         }])

        self.assertEqual(CoreUser.objects.count(), 6)

        appointments = Appointment.objects.filter(
            name=u'Besichtigung Anlage Müller, Düsseldorf')
        self.assertEqual(appointments.count(), APPOINTMENT_REPEAT_DAYS)
        difference_dates = (appointments[1].start_date -
                            appointments[0].start_date)
        self.assertEqual(difference_dates, datetime.timedelta(days=1))
        self.assertEqual(Product.objects.count(), 8)

    def test_load_demo_data(self):
        args = ['--demo']
        opts = {}
        call_command('loadkupferinitialdata', *args, **opts)
        self._check_demo_data()

    def test_load_demo_data_two_times_crashes_but_db_keeps_consistent(self):
        args = ['--demo']
        opts = {}
        call_command('loadkupferinitialdata', *args, **opts)

        User.objects.all().delete()

        with self.assertRaises(ValidationError):
            call_command('loadkupferinitialdata', *args, **opts)

        self.assertRaises(User.DoesNotExist, User.objects.get,
                          first_name="Horst", last_name="Lehmann")

    def test_load_demo_data_and_restore_does_not_crash(self):
        args = ['--demo']
        opts = {}
        call_command('loadkupferinitialdata', *args, **opts)
        self._check_demo_data()

        # Just to double check sequences later
        factories.WorkflowLevel2.create_batch(20)

        args = ['--restore']
        opts = {}
        call_command('loadkupferinitialdata', *args, **opts)

        # We check that we don't have repeated data and that sequences are
        # reset.
        total_wflvl2 = WorkflowLevel2.objects.all().count()
        self.assertEqual(total_wflvl2, 20)

        expected_next = total_wflvl2 + 1
        wflvl2_next = factories.WorkflowLevel2()
        self.assertEqual(wflvl2_next.id, expected_next)
