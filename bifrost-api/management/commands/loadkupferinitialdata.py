# -*- coding: utf-8 -*-
from cStringIO import StringIO
from datetime import datetime, timedelta
import logging
import os

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError, connection
import factories
import pytz
from workflow.models import (
    ROLE_VIEW_ONLY, ROLE_ORGANIZATION_ADMIN, ROLE_PROGRAM_ADMIN,
    ROLE_PROGRAM_TEAM, Organization, WorkflowLevel1, CoreUser, Group,
    WorkflowLevel2, WorkflowTeam)

logger = logging.getLogger(__name__)
DEFAULT_ORG = {
    'id': 1,
    'name': settings.DEFAULT_ORG,
}
DEFAULT_PROGRAM_NAME = 'Default Program'
APPOINTMENT_REPEAT_DAYS = 365  # days that the same appointment repeats


class Command(BaseCommand):
    help = """
    Loads initial factories data for Kupfer.

    By default, a new default organization will be created with a default
    program.

    Passing a --demo flag will populate the database with extra sample
    projects, users, contacts and appointments.

    Passing a --restore flag will restore the demo data.
    """
    APPS = ('appointment', 'auth', 'contact', 'workflow')

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        # Note: for the lists we fill the first element with an empty value for
        # development readability (id == position).
        self._organization = None
        self._groups = ['']
        self._addresses = ['']
        self._workflowlevel1 = None
        self._workflowlevel2s = ['']
        self._contacts = ['']
        self._tolausers = ['']

    def _clear_database(self):
        """
        Clears all old data except:
        - Default organization
        - Default workflowlevel1
        - Current registered users

        Before everything happens, current registered users will be reassigned
        to the default organization and to have residency in Germany.
        """
        # Check integrity
        try:
            organization = Organization.objects.get(**DEFAULT_ORG)
        except Organization.DoesNotExist:
            msg = ("Error: the default organization could not be found in the "
                   "database. Maybe you are restoring without having run the "
                   "command a first time?")
            logger.error(msg)
            self.stderr.write("{}\n".format(msg))
            raise IntegrityError(msg)

        # Reassign organization and country for current registered users
        CoreUser.objects.all().update(organization=organization)

        # Delete data - Kill 'Em All!
        Organization.objects.exclude(id=DEFAULT_ORG['id']).delete()
        Group.objects.all().delete()
        WorkflowLevel1.objects.exclude(name=DEFAULT_PROGRAM_NAME).delete()
        WorkflowLevel1.objects.all().delete()
        WorkflowLevel2.history.all().delete()
        WorkflowLevel2.objects.all().delete()
        WorkflowTeam.objects.all().delete()

    def _create_organization(self):
        try:
            self._organization = Organization.objects.get(**DEFAULT_ORG)
        except Organization.DoesNotExist:
            self._organization = factories.Organization(
                id=DEFAULT_ORG['id'],
                name=DEFAULT_ORG['name'],
                organization_url="https://www.humanitec.com",
                level_2_label="Project",
                level_3_label="Activity",
                level_4_label="Component",
            )

    def _create_site(self):
        site = Site.objects.get(id=1)
        site.domain = 'humanitec.com'
        site.name = 'API'
        site.save()

        factories.CoreSites(site=get_current_site(None))

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

    def _create_workflowlevel1(self):
        self._workflowlevel1 = WorkflowLevel1.objects.get_or_create(
            name=DEFAULT_PROGRAM_NAME, organization=self._organization)[0]


    def _create_workflowlevel2s(self):
        workflowlevel2s = (
            (u'Umbau Heizungsanlage', 'open'),
            (u'Installation Boiler', 'awaitingapproval'),
            (u'Sanierung Zentralheizung', 'inprogress'),
            (u'Reparatur Wärmepumpe', 'invoiced'),
            (u'Wartung Gasetagenheizung', 'inprogress'),
            (u'Neueinbau Pelletheizung', 'inprogress'),
            (u'Wartung Kessel und Therme', 'awaitingapproval'),
            (u'Modernisierung Ölheizung', 'inprogress'),
            (u'Einbau Fußbodenheizung', 'invoiced'),
            (u'Umbau Heizungsanlage', 'inprogress'),
            (u'Installation Boiler', 'invoiced'),
            (u'Sanierung Zentralheizung', 'open'),
            (u'Reparatur Wärmepumpe', 'open'),
            (u'Wartung Gasetagenheizung', 'awaitingapproval'),
            (u'Neueinbau Pelletheizung', 'inprogress'),
            (u'Wartung Kessel und Therme', 'invoiced'),
            (u'Modernisierung Ölheizung', 'open'),
            (u'Einbau Fußbodenheizung', 'awaitingapproval'),
            (u'Reparatur Wärmepumpe', 'open'),
            (u'Wartung Gasetagenheizung', 'awaitingapproval'),
        )

        for i, workflowlevel2 in enumerate(workflowlevel2s):
            name, progress = workflowlevel2
            self._workflowlevel2s.append(factories.WorkflowLevel2(
                id=i+1,
                workflowlevel1=self._workflowlevel1,
                name=name,
                progress=progress,
                address=self._addresses[i+1],
            ))

    def _create_contacts(self):
        contacts = (
            (u'Peter', u'Müller', '+491749939951', [1, 2, 3, 4]),
            (u'Michael', u'Schmidt', '+491584438554', [5, 6, 7]),
            (u'Thomas', u'Schneider', '+491541608697', [8, 9, 10]),
            (u'Andreas', u'Fischer', '+491692748623', [11, 12, 13]),
            (u'Uwe', u'Weber', '+491756297899', [14, 15, 16]),
            (u'Klaus', u'Meyer', '+491660156707', [17, 18]),
            (u'Jürgen', u'Wagner', '+491709068743', [19, 20]),
            (u'Günther', u'Becker', '+491749524702', []),
            (u'Stefan', u'Schulz', '+491553975959', []),
            (u'Christian', u'Hoffmann', '+491729044373', []),
            (u'Helga', u'Schäfer', '+491679390126', []),
            (u'Susanne', u'Koch', '+491774113801', []),
            (u'Ursula', u'Bauer', '+491577836745', []),
            (u'Sabine', u'Richter', '+491558612433', []),
            (u'Renate', u'Klein', '+491656395828', []),
            (u'Ingrid', u'Wolf', '+491631792599', []),
            (u'Monika', u'Schröder', '+491584821944', []),
            (u'Karin', u'Neumann', '+491684348932', []),
            (u'Gisela', u'Schwarz', '+491666781950', []),
            (u'Petra', u'Zimmermann', '+491649808408', [])
        )

        for i, contact in enumerate(contacts):
            first_name, last_name, phone, workflowlevel2s = contact
            address = self._addresses[i+1]
            address['type'] = 'home'
            organization_uuid = str(self._organization.organization_uuid)
            workflowlevel2_uuids = [
                self._workflowlevel2s[j].level2_uuid for j in workflowlevel2s]
            self._contacts.append(contact_factories.Contact(
                id=i+1,
                organization_uuid=organization_uuid,
                workflowlevel1_uuids=[str(self._workflowlevel1.level1_uuid)],
                workflowlevel2_uuids=workflowlevel2_uuids,
                first_name=first_name,
                last_name=last_name,
                phones=[{'type': 'mobile', 'number': phone, }],
                addresses=[address],
            ))

    def _create_products(self):
        products = (
            (u'Bosch', u'Boiler', u'Wandheizzentrale WTC-GW',
             self._workflowlevel2s[1]),
            (u'Bosch', u'Boiler', u'Ölbrenner WL10/2-D/Z',
             self._workflowlevel2s[2]),
            (u'Viessmann', u'Boiler', u'Vitodens 343-F',
             self._workflowlevel2s[3]),
            (u'Vaillant', u'Wärmepumpe', u'flexoTHERM exclusive',
             self._workflowlevel2s[4]),
            (u'Vaillant', u'Gasheizung', u'Gas-Brennwertsystem ecoCOMPACT',
             self._workflowlevel2s[5]),
            (u'-', None, u'atmoTEC plus VCW 194', self._workflowlevel2s[7]),
            (u'Viessmann', u'Boiler', u'Vitodens 300',
             self._workflowlevel2s[10]),
            (u'-', None, u'Logano plus KB192i-50', self._workflowlevel2s[12]),
        )

        for i, product in enumerate(products):
            name, type, reference_id, workflowlevel2 = product
            factories.Product(id=i+1, workflowlevel2=workflowlevel2, name=name,
                              type=type, reference_id=reference_id)

    def _create_tolausers(self):
        tolausers = (
            (u'Horst', u'Lehmann'),
            (u'Frank', u'Hahn'),
            (u'Dieter', u'König'),
            (u'Angelika', u'Huber'),
            (u'Brigitte', u'Peters'),
            (u'Andrea', u'Scholz')
        )

        for i, tolauser in enumerate(tolausers):
            first_name, last_name = tolauser
            user = factories.User(
                first_name=first_name,
                last_name=last_name,
                username=first_name+last_name)
            user.set_password('notbrass')
            user.save()

            self._tolausers.append(factories.CoreUser(
                id=i+1,
                user=user,
                organization=self._organization
            ))

    def _create_appointments(self):
        now = datetime.now(pytz.utc)
        appointments = (
            (u'Besichtigung Anlage Müller, Düsseldorf',
             datetime(now.year, now.month, now.day, 8, 0, tzinfo=pytz.UTC),
             datetime(now.year, now.month, now.day, 11, 0, tzinfo=pytz.UTC),
             self._contacts[1].uuid,
             self._workflowlevel2s[1],
             [self._tolausers[1].tola_user_uuid]
             ),
            (u'Aufmaß',
             datetime(now.year, now.month, now.day, 13, 0, tzinfo=pytz.UTC),
             datetime(now.year, now.month, now.day, 15, 0, tzinfo=pytz.UTC),
             self._contacts[2].uuid,
             self._workflowlevel2s[6],
             [self._tolausers[1].tola_user_uuid]),
            (u'Wartung atmoTEC plus VCW 194, Mainz',
             datetime(now.year, now.month, now.day, 9, 0, tzinfo=pytz.UTC),
             datetime(now.year, now.month, now.day, 13, 0, tzinfo=pytz.UTC),
             self._contacts[2].uuid,
             self._workflowlevel2s[7],
             [self._tolausers[2].tola_user_uuid,
              self._tolausers[3].tola_user_uuid]),
            (u'Installation Vitodens 300',
             datetime(now.year, now.month, now.day, 14, 30, tzinfo=pytz.UTC),
             datetime(now.year, now.month, now.day, 18, 0, tzinfo=pytz.UTC),
             self._contacts[3].uuid,
             self._workflowlevel2s[10],
             [self._tolausers[2].tola_user_uuid]),
            (u'Urlaub',
             datetime(now.year, now.month, now.day, 7, 0, tzinfo=pytz.UTC),
             datetime(now.year, now.month, now.day, 18, 0, tzinfo=pytz.UTC),
             None,
             self._workflowlevel2s[11],
             [self._tolausers[4].tola_user_uuid]),
            (u'Umbau Logano plus KB192i-50',
             datetime(now.year, now.month, now.day, 7, 0, tzinfo=pytz.UTC),
             datetime(now.year, now.month, now.day, 16, 0, tzinfo=pytz.UTC),
             self._contacts[4].uuid,
             self._workflowlevel2s[12],
             [self._tolausers[5].tola_user_uuid]
             ),
        )

        i = 1
        for appointment in appointments:
            name, start_date, end_date, contact, wf2s, invitees = appointment
            for day_sum in range(APPOINTMENT_REPEAT_DAYS):
                appointment_factories.Appointment(
                    id=i,
                    name=name,
                    contact_uuid=contact,
                    organization_uuid=self._organization.organization_uuid,
                    owner=self._tolausers[1].user,
                    start_date=start_date + timedelta(days=day_sum),
                    end_date=end_date + timedelta(days=day_sum),
                    workflowlevel2=[wf2s],
                    invitee_uuids=invitees,
                )
                i += 1

    def _reset_sql_sequences(self):
        """
        After adding to database all rows using hardcoded IDs, the primary key
        counter of each table is not autoupdated. This method resets all
        primary keys for all affected apps.
        """
        os.environ['DJANGO_COLORS'] = 'nocolor'

        for app in self.APPS:
            buf = StringIO()
            call_command('sqlsequencereset', app, stdout=buf)

            buf.seek(0)
            sql_commands = buf.getvalue().splitlines()

            sql_commands_clean = []
            for command in sql_commands:
                # As we are already inside a transaction thanks to the
                # transaction.atomic decorator, we don't need
                # the COMMIT and BEGIN statements. If there was some problem
                # we are automatically rolling back the transaction.
                if command not in ('COMMIT;', 'BEGIN;'):
                    sql_commands_clean.append(command)

            cursor = connection.cursor()
            cursor.execute("\n".join(sql_commands_clean))

    def _assign_workflowteam_current_users(self):
        role = Group.objects.get(name=ROLE_PROGRAM_ADMIN)
        tola_user_ids = CoreUser.objects.values_list('id', flat=True).all()

        wfteams = [
            WorkflowTeam(workflow_user_id=user_id, role=role,
                         workflowlevel1=self._workflowlevel1)
            for user_id in tola_user_ids
        ]
        WorkflowTeam.objects.bulk_create(wfteams)

    def add_arguments(self, parser):
        parser.add_argument('--demo', action='store_true',
                            help='Loads extra demo data')
        parser.add_argument('--restore', action='store_true',
                            help=('Restores back demo data deleting old '
                                  'previous one (except users)'))

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEFAULT_ORG:
            msg = ('A DEFAULT_ORG needs to be set up in the configuration to '
                   'run the script.')
            logger.error(msg)
            self.stderr.write("{}\n".format(msg))
            raise ImproperlyConfigured(msg)

        if not settings.CREATE_DEFAULT_PROGRAM:
            msg = ('A CREATE_DEFAULT_PROGRAM needs to be set up in the '
                   'configuration to run the script.')
            logger.error(msg)
            self.stderr.write("{}\n".format(msg))
            raise ImproperlyConfigured(msg)

        if options['restore']:
            self.stdout.write('Clearing up database')
            self._clear_database()

        self.stdout.write('Creating basic data')
        self._create_organization()
        self._create_site()
        self._create_groups()
        self._create_workflowlevel1()

        if options['demo'] or options['restore']:
            self.stdout.write('Creating demo data')
            try:
                self._populate_addresses()
                self._create_workflowlevel2s()
                self._create_contacts()
                self._create_products()
                self._create_tolausers()
                self._create_appointments()
            except (IntegrityError, ValidationError):
                msg = ("Error: the data could not be populated in the "
                       "database. Check that the affected database tables are "
                       "empty.")
                logger.error(msg)
                self.stderr.write("{}\n".format(msg))
                raise

        self.stdout.write('Resetting SQL sequences')
        self._reset_sql_sequences()

        if options['restore']:
            self.stdout.write('Assigning current users to created projects')
            self._assign_workflowteam_current_users()
