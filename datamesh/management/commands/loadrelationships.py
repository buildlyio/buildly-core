import json

from django.core.management import BaseCommand

from datamesh.models import JoinRecord, Relationship, LogicModuleModel
from core.models import LogicModule, Organization

DEFAULT_FILE_NAME = 'data/contacts.json'


class Command(BaseCommand):
    help = """
    Load relationships from a file, which should be named 'contacts.json' or specify the name with the --file parameter.

    To get the file, get the pod-name of the crm_service in your kubernetes namespace and run:
        kubectl exec -n <namespace> -it <pod-name> -- bash -c "python manage.py dumpdata
            --format=json --indent=4 contact.Contact" > contacts.json

    Example:
    kubectl exec -n kupfer-dev -it crm-service-cf5576999-vj5s4 -- bash -c "python manage.py dumpdata --format=json --indent=4 contact.Contact" > data/contacts.json
    kubectl cp data/contacts.json kupfer-dev/buildly-7b96bb7487-f7c6m:/code/contacts.json
    kubectl exec -n kupfer-dev -it buildly-7b96bb7487-f7c6m bash -- -c "python manage.py loadrelationships --file=contacts.json"
    """  # noqa

    counter = 0

    def add_arguments(self, parser):
        """Add --file argument to Command."""
        parser.add_argument(
            '--file', default=None, nargs='?', help='Path of file to import.'
        )

    def handle(self, *args, **options):
        """
        Load contacts with siteprofile_uuids from file and write the data directly
        into the JoinRecords.
        """
        filename = options.get('file')
        if not filename:
            filename = DEFAULT_FILE_NAME
        with open(filename, 'r', encoding='utf-8') as contacts_file:
            contacts = json.load(contacts_file)
        crm_logic_module = LogicModule.objects.get(endpoint_name='crm')
        location_logic_module = LogicModule.objects.get(endpoint_name='location')

        origin_model, _ = LogicModuleModel.objects.get_or_create(
            model='Contact',
            logic_module_endpoint_name=crm_logic_module.endpoint_name,
            endpoint='/contact/',
            lookup_field_name='uuid',
        )
        related_model, _ = LogicModuleModel.objects.get_or_create(
            model='SiteProfile',
            logic_module_endpoint_name=location_logic_module.endpoint_name,
            endpoint='/siteprofiles/',
            lookup_field_name='uuid',
        )
        relationship, _ = Relationship.objects.get_or_create(
            origin_model=origin_model,
            related_model=related_model,
            key='contact_siteprofile_relationship',
        )
        eligible_join_records = []
        # create JoinRecords with contact.id and siteprofile_uuid for all contacts
        for contact in contacts:
            organization_uuid = contact['fields']['organization_uuid']
            try:
                organization = Organization.objects.get(pk=organization_uuid)
            except Organization.DoesNotExist:
                print(f'Organization({organization_uuid}) not found.')
                continue
            self.counter += 1
            siteprofile_uuids = contact['fields']['siteprofile_uuids']
            if not siteprofile_uuids:
                continue
            for siteprofile_uuid in json.loads(siteprofile_uuids):
                join_record, _ = JoinRecord.objects.get_or_create(
                    relationship=relationship,
                    record_uuid=contact['pk'],
                    related_record_uuid=siteprofile_uuid,
                    defaults={'organization': organization},
                )
                print(join_record)
                eligible_join_records.append(join_record.pk)
        print(f'{self.counter} Contacts parsed and written to the JoinRecords.')
        # delete not eligible JoinRecords in this relationship
        deleted, _ = (
            JoinRecord.objects.exclude(pk__in=eligible_join_records)
            .filter(relationship=relationship)
            .delete()
        )
        print(f'{deleted} JoinRecord(s) deleted.')
