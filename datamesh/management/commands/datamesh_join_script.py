import json
import re

from datamesh.models import JoinRecord, Relationship, LogicModuleModel
from core.models import LogicModule

"""
# add logic module from core
    origin_logic_module = logic module from core
    related_logic_module = logic module from core

# send is_local =True/False if join is it with core

# origin_module_model = send Model name of origin
# origin_module_endpoint = send origin module endpoint
# origin_module_lookup_field_name = send origin module model lookup field

# related_module_model = send Model name of origin
# related_module_endpoint = send origin module endpoint
# related_module_lookup_field_name = send origin module model lookup field

# fk_field_name = foreign key name

# lookup_field_type = it's either id or uuid
# relationship_key_name = send relation name

# field_name = send field of json file which want to join with
# is_list = True/False if the field type is array then send it True else False

# organization = send organization name if have else by default it will set to None

join_relationship(
        json_file="product.json",

        is_local=False,

        origin_logic_module='product',
        related_logic_module='product',

        origin_module_model='Product',
        origin_module_endpoint='/product/',
        origin_module_lookup_field_name='product_uuid',

        related_module_model='ThirdPartyTool',
        related_module_endpoint='/thirdpartytool/',
        related_module_lookup_field_name='thirdpartytool_uuid',

        fk_field_name='third_party_tool',

        origin_lookup_field_type='uuid',
        related_lookup_field_type='uuid',

        relationship_key_name='product_thirdpartytool_relationship',
        field_name='third_party_tool',
        is_list=True,
        organization=None,
)
"""

"""
join_relationship will accept above data to create datamesh relation and from JSON file it will create join for 
existing objects.
"""


def join_relationship(*args, **kwargs):
    is_file_exists = True
    if kwargs.get('json_file'):
        model_json_file = str(kwargs.get('json_file'))

        # load json file and take data into model_data variable
        try:
            with open(model_json_file, 'r', encoding='utf-8') as file_data:
                model_data = json.load(file_data)
        except FileNotFoundError:
            is_file_exists = False
            print(f'file {model_json_file} not found !!')
    else:
        pass

    # create relationship,origin and related model
    relationship, _ = prepare_relation(**kwargs)

    print(f'created relation : {relationship}')

    eligible_join_records = []
    counter = 0

    # iterate over loaded JSON data
    if is_file_exists:
        for related_data in model_data:

            field_value = related_data['fields'][kwargs.get('field_name')]

            if not field_value:
                continue

            # convert uuid string to list
            if kwargs.get('related_lookup_field_type') == 'uuid':
                value_list = re.findall(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){4}[0-9a-f]{8}', field_value)
            else:
                value_list = field_value if not kwargs.get('is_list') else json.loads(field_value)

            # iterate over item_ids
            for field_value in value_list:
                join_record = join_record_datamesh(
                    relationship=relationship,
                    pk=related_data['pk'],
                    field_value=field_value,
                    organization=kwargs.get('organization'),
                    origin_lookup_field_type=kwargs.get('origin_lookup_field_type'),
                    related_lookup_field_type=kwargs.get('related_lookup_field_type'),
                )
                counter += 1

                print(join_record)
                eligible_join_records.append(join_record.pk)

        print(f'{counter}  parsed and written to the JoinRecords.')


def prepare_relation(*args, **kwargs):
    """This function will create logic module and datamesh relationship"""

    # get logic module from core
    origin_logic_module = LogicModule.objects.get(endpoint_name=str(kwargs.get('origin_logic_module')))

    if not kwargs.get('is_local'):
        related_logic_module = LogicModule.objects.get(endpoint_name=str(kwargs.get('related_logic_module')))
        related_module_name = related_logic_module.endpoint_name
    else:
        related_module_name = 'core'

    # get or create datamesh Logic Module Model
    origin_model, _ = LogicModuleModel.objects.get_or_create(
        model=str(kwargs.get('origin_module_model')),
        logic_module_endpoint_name=origin_logic_module.endpoint_name,
        endpoint=str(kwargs.get('origin_module_endpoint')),
        lookup_field_name=str(kwargs.get('origin_module_lookup_field_name')),
    )

    # get or create datamesh Logic Module Model
    related_model, _ = LogicModuleModel.objects.get_or_create(
        model=str(kwargs.get('related_module_model')),
        logic_module_endpoint_name=related_module_name,
        endpoint=str(kwargs.get('related_module_endpoint')),
        lookup_field_name=str(kwargs.get('related_module_lookup_field_name')),
        is_local=kwargs.get('is_local'),
    )

    # get or create relationship of origin_model and related_model in datamesh
    relationship, _ = Relationship.objects.get_or_create(
        origin_model=origin_model,
        related_model=related_model,
        key=str(kwargs.get('relationship_key_name')),
        fk_field_name=kwargs.get('fk_field_name'),
    )
    return relationship, _


def join_record_datamesh(*args, **kwargs):
    if kwargs.get('origin_lookup_field_type') == 'id' and kwargs.get('related_lookup_field_type') == 'id':
        relation_value = {
            "record_id": kwargs.get('pk'),
            "related_record_id": kwargs.get('field_value')
        }

    elif kwargs.get('origin_lookup_field_type') == 'uuid' and kwargs.get('related_lookup_field_type') == 'uuid':
        relation_value = {
            "record_uuid": kwargs.get('pk'),
            "related_record_uuid": kwargs.get('field_value')
        }

    elif kwargs.get('origin_lookup_field_type') == 'uuid' and kwargs.get('related_lookup_field_type') == 'id':
        relation_value = {
            "record_uuid": kwargs.get('pk'),
            "related_record_id": kwargs.get('field_value')
        }

    elif kwargs.get('origin_lookup_field_type') == 'id' and kwargs.get('related_lookup_field_type') == 'uuid':
        relation_value = {
            "record_id": kwargs.get('pk'),
            "related_record_uuid": kwargs.get('field_value')
        }
    else:
        relation_value = None

    join_record, _ = JoinRecord.objects.get_or_create(
        relationship=kwargs.get('relationship'),
        **relation_value,
        defaults={
            'organization': kwargs.get('organization') if kwargs.get('organization') else None
        }
    )
    return join_record
