import json

from django.core.management import BaseCommand

from datamesh.models import JoinRecord, Relationship, LogicModuleModel
from gateway.models import LogicModule
from workflow.models import Organization

DEFAULT_FILE_NAME = 'data/contacts.json'


class Command(BaseCommand):
    help = """
    Load relationships from a file, which should be named 'contacts.json' or specify the name with the --file parameter.

    To get the file, get the pod-name of the crm_service in your kubernetes namespace and run:
        kubectl exec -n <namespace> -it <pod-name> -- bash -c "python manage.py dumpdata
            --format=json --indent=4 contact.Contact" > contacts.json

    Example:
    kubectl exec -n kupfer-dev -it crm-service-cf5576999-vj5s4 -- bash -c "python manage.py dumpdata --format=json --indent=4 contact.Contact" > data/contacts.json
    kubectl cp data/contacts.json kupfer-dev/bifrost-7b96bb7487-f7c6m:/code/contacts.json
    kubectl exec -n kupfer-dev -it bifrost-7b96bb7487-f7c6m bash -- -c "python manage.py loadrelationships --file=contacts.json"
    """  # noqa

    counter = 0

    def add_arguments(self, parser):
        """Add --file argument to Command."""
        parser.add_argument(
            '--file', default=None, nargs='?', help='Path of file to import.',
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
            logic_module=crm_logic_module
        )
        related_model, _ = LogicModuleModel.objects.get_or_create(
            model='SiteProfile',
            logic_module=location_logic_module
        )
        relationship, _ = Relationship.objects.get_or_create(
            origin_model=origin_model,
            related_model=related_model,
            key='siteprofile_relationship'
        )
        # create JoinRecords with contact.id and siteprofile_uuid for all contacts
        for contact in contacts:
            try:
                organization = Organization.objects.get(pk=contact['fields']['organization_uuid'])
            except Organization.DoesNotExist:
                break
            self.counter += 1
            for siteprofile_uuid in json.loads(contact['fields']['siteprofile_uuids']):
                join_record, _ = JoinRecord.objects.get_or_create(
                    relationship=relationship,
                    record_id=contact['pk'],
                    related_record_uuid=siteprofile_uuid,
                    defaults={'organization': organization}
                )
                print(join_record)
        print(f'{self.counter} Contacts parsed and written to the JoinRecords.')
