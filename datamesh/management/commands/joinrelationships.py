from django.core.management.base import BaseCommand
from datamesh.management.commands.datamesh_join_script import join_relationship


class Command(BaseCommand):

    def add_arguments(self, parser):
        """Add --file argument to Command."""
        parser.add_argument(
            '--file', default=None, nargs='?', help='Path of file to import.',
        )

    def handle(self, *args, **options):
        run_seed(self, options['file'])


def run_seed(self, mode):
    """call function here."""

    # product <-> product_tool - within service model join.
    join_relationship(
        json_file="product.json",

        is_local=False,

        origin_logic_module='product',
        related_logic_module='product',

        origin_module_model='Product',
        origin_module_endpoint='/product/',
        origin_module_lookup_field_name='product_uuid',

        related_module_model='ProductTools',
        related_module_endpoint='/producttools/',
        related_module_lookup_field_name='product_tool_uuid',

        origin_lookup_field_type='uuid',
        related_lookup_field_type='uuid',

        relationship_key_name='product_product_tool_relationship',
        field_name='product_tool',
        is_list=False,
        organization=None,
    )

    # product <-> product_team - within service model join.
    join_relationship(
        json_file="product.json",

        is_local=False,

        origin_logic_module='product',
        related_logic_module='product',

        origin_module_model='Product',
        origin_module_endpoint='/product/',
        origin_module_lookup_field_name='product_uuid',

        related_module_model='ProductTeam',
        related_module_endpoint='/productteam/',
        related_module_lookup_field_name='product_team_uuid',

        origin_lookup_field_type='uuid',
        related_lookup_field_type='uuid',

        relationship_key_name='product_product_team_relationship',

        field_name='product_team',
        is_list=False,
        organization=None,
    )

    # product_tool <-> users -  service and core model join.
    join_relationship(
        json_file="ProductTeam.json",

        is_local=True,

        origin_logic_module='product',
        related_logic_module='product',

        origin_module_model='ProductTools',
        origin_module_endpoint='/producttools/',
        origin_module_lookup_field_name='product_tool_uuid',

        related_module_model='CoreUser',
        related_module_endpoint='/coreuser/',
        related_module_lookup_field_name='core_user_uuid',

        origin_lookup_field_type='uuid',
        related_lookup_field_type='uuid',

        relationship_key_name='product_user_relationship',
        field_name='users',
        is_list=True,
        organization=None,
    )
