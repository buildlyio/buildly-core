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

    # # product <-> organization - with core model join.
    # """product.json"""
    # join_relationship(
    #     json_file="product.json",
    #
    #     is_local=True,
    #
    #     origin_logic_module='product',
    #     related_logic_module='core',
    #
    #     origin_module_model='Product',
    #     origin_module_endpoint='/product/',
    #     origin_module_lookup_field_name='product_uuid',
    #
    #     related_module_model='Organization',
    #     related_module_endpoint='/organization/',
    #     related_module_lookup_field_name='organization_uuid',
    #
    #     fk_field_name='organization_uuid',
    #
    #     origin_lookup_field_type='uuid',
    #     related_lookup_field_type='uuid',
    #
    #     relationship_key_name='product_organization_relationship',
    #     field_name='organization_uuid',
    #     is_list=False,
    #     organization=None,
    # )

    # product <-> third party tool - within service model join.
    """product.json"""
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

    # product <-> product_team - within service model join.
    """product.json"""
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
        related_module_lookup_field_name='productteam_uuid',

        fk_field_name='product_team',

        origin_lookup_field_type='uuid',
        related_lookup_field_type='uuid',

        relationship_key_name='product_product_team_relationship',

        field_name='product_team',
        is_list=False,
        organization=None,
    )

    # credential <-> product within service model join.
    """credential.json"""
    join_relationship(
        json_file="credential.json",

        is_local=False,

        origin_logic_module='product',
        related_logic_module='product',

        origin_module_model='Credential',
        origin_module_endpoint='/credential/',
        origin_module_lookup_field_name='credential_uuid',

        related_module_model='Product',
        related_module_endpoint='/product/',
        related_module_lookup_field_name='product_uuid',

        fk_field_name='product_uuid',

        origin_lookup_field_type='uuid',
        related_lookup_field_type='uuid',

        relationship_key_name='credential_product_relationship',

        field_name='product_uuid',
        is_list=False,
        organization=None,
    )

    # release <-> product within service model join.
    """release.json"""
    join_relationship(
        json_file="release.json",

        is_local=False,

        origin_logic_module='product',
        related_logic_module='product',

        origin_module_model='Release',
        origin_module_endpoint='/release/',
        origin_module_lookup_field_name='release_uuid',

        related_module_model='Product',
        related_module_endpoint='/product/',
        related_module_lookup_field_name='product_uuid',

        fk_field_name='product_uuid',

        origin_lookup_field_type='uuid',
        related_lookup_field_type='uuid',

        relationship_key_name='release_product_relationship',

        field_name='product_uuid',
        is_list=False,
        organization=None,
    )

    # release <-> module within  service model join.
    """release.json"""
    join_relationship(
        json_file="release.json",

        is_local=False,

        origin_logic_module='product',
        related_logic_module='product',

        origin_module_model='Release',
        origin_module_endpoint='/release/',
        origin_module_lookup_field_name='release_uuid',

        related_module_model='Module',
        related_module_endpoint='/module/',
        related_module_lookup_field_name='module_uuid',

        fk_field_name='modules_uuid',

        origin_lookup_field_type='uuid',
        related_lookup_field_type='uuid',

        relationship_key_name='release_module_relationship',

        field_name='modules_uuid',
        is_list=False,
        organization=None,
    )

    # release <-> dev team with two different service model join.
    """release.json"""
    join_relationship(
        json_file="release.json",

        is_local=False,

        origin_logic_module='product',
        related_logic_module='devpartner',

        origin_module_model='Release',
        origin_module_endpoint='/release/',
        origin_module_lookup_field_name='release_uuid',

        related_module_model='DevTeam',
        related_module_endpoint='/devteam/',
        related_module_lookup_field_name='devteam_uuid',

        fk_field_name='dev_team_uuid',

        origin_lookup_field_type='uuid',
        related_lookup_field_type='uuid',

        relationship_key_name='release_dev_team_relationship',

        field_name='dev_team_uuid',
        is_list=True,
        organization=None,
    )

    #######################################################################

    # decision <-> feature team within service model join.
    """decision.json"""
    join_relationship(
        json_file="decision.json",

        is_local=False,

        origin_logic_module='decision',
        related_logic_module='decision',

        origin_module_model='Decision',
        origin_module_endpoint='/decision/',
        origin_module_lookup_field_name='decision_uuid',

        related_module_model='Feature',
        related_module_endpoint='/feature/',
        related_module_lookup_field_name='feature_uuid',

        fk_field_name='feature',

        origin_lookup_field_type='uuid',
        related_lookup_field_type='uuid',

        relationship_key_name='decision_feature_relationship',

        field_name='feature',
        is_list=False,
        organization=None,
    )

    # decision <-> issue team within service model join.
    """decision.json"""
    join_relationship(
        json_file="decision.json",

        is_local=False,

        origin_logic_module='decision',
        related_logic_module='decision',

        origin_module_model='Decision',
        origin_module_endpoint='/decision/',
        origin_module_lookup_field_name='decision_uuid',

        related_module_model='Issue',
        related_module_endpoint='/issue/',
        related_module_lookup_field_name='issue_uuid',

        fk_field_name='issue',

        origin_lookup_field_type='uuid',
        related_lookup_field_type='uuid',

        relationship_key_name='decision_issue_relationship',

        field_name='issue',
        is_list=False,
        organization=None,
    )

    # feature <-> status  team within service model join.
    """feature.json"""
    join_relationship(
        json_file="feature.json",

        is_local=False,

        origin_logic_module='decision',
        related_logic_module='decision',

        origin_module_model='Feature',
        origin_module_endpoint='/feature/',
        origin_module_lookup_field_name='feature_uuid',

        related_module_model='Status',
        related_module_endpoint='/status/',
        related_module_lookup_field_name='status_uuid',

        fk_field_name='status',

        origin_lookup_field_type='uuid',
        related_lookup_field_type='uuid',

        relationship_key_name='feature_status_relationship',

        field_name='status',
        is_list=False,
        organization=None,
    )

    # issue <-> feature team within service model join.
    """issue.json"""
    join_relationship(
        json_file="issue.json",

        is_local=False,

        origin_logic_module='decision',
        related_logic_module='decision',

        origin_module_model='Issue',
        origin_module_endpoint='/issue/',
        origin_module_lookup_field_name='issue_uuid',

        related_module_model='Feature',
        related_module_endpoint='/feature/',
        related_module_lookup_field_name='feature_uuid',

        fk_field_name='feature_uuid',

        origin_lookup_field_type='uuid',
        related_lookup_field_type='uuid',

        relationship_key_name='issue_feature_relationship',

        field_name='feature_uuid',
        is_list=False,
        organization=None,
    )

    # issue <-> status team within service model join.
    """issue.json"""
    join_relationship(
        json_file="issue.json",

        is_local=False,

        origin_logic_module='decision',
        related_logic_module='decision',

        origin_module_model='Issue',
        origin_module_endpoint='/issue/',
        origin_module_lookup_field_name='issue_uuid',

        related_module_model='Status',
        related_module_endpoint='/status/',
        related_module_lookup_field_name='status_uuid',

        fk_field_name='status',

        origin_lookup_field_type='uuid',
        related_lookup_field_type='uuid',

        relationship_key_name='issue_status_relationship',

        field_name='status',
        is_list=False,
        organization=None,
    )

    # feedback <-> issue team within service model join.
    """feedback.json"""
    join_relationship(
        json_file="feedback.json",

        is_local=False,

        origin_logic_module='decision',
        related_logic_module='decision',

        origin_module_model='Feedback',
        origin_module_endpoint='/feedback/',
        origin_module_lookup_field_name='feedback_uuid',

        related_module_model='Issue',
        related_module_endpoint='/issue/',
        related_module_lookup_field_name='issue_uuid',

        fk_field_name='issue',

        origin_lookup_field_type='uuid',
        related_lookup_field_type='uuid',

        relationship_key_name='feedback_issue_relationship',

        field_name='issue',
        is_list=False,
        organization=None,
    )

    # feedback <-> feature team within service model join.
    """feedback.json"""
    join_relationship(
        json_file="feedback.json",

        is_local=False,

        origin_logic_module='decision',
        related_logic_module='decision',

        origin_module_model='Feedback',
        origin_module_endpoint='/feedback/',
        origin_module_lookup_field_name='feedback_uuid',

        related_module_model='Feature',
        related_module_endpoint='/feature/',
        related_module_lookup_field_name='feature_uuid',

        fk_field_name='feature',

        origin_lookup_field_type='uuid',
        related_lookup_field_type='uuid',

        relationship_key_name='feedback_feature_relationship',

        field_name='feature',
        is_list=False,
        organization=None,
    )

    # timesheethour <-> timesheet team within service model join.
    """timesheethour.json"""
    join_relationship(
        json_file="timesheethour.json",

        is_local=False,

        origin_logic_module='devpartner',
        related_logic_module='devpartner',

        origin_module_model='TimeSheetHour',
        origin_module_endpoint='/timesheethour/',
        origin_module_lookup_field_name='timesheethour_uuid',

        related_module_model='TimeSheet',
        related_module_endpoint='/timesheet/',
        related_module_lookup_field_name='timesheet_uuid',

        fk_field_name='timesheet_uuid',

        origin_lookup_field_type='uuid',
        related_lookup_field_type='uuid',

        relationship_key_name='timesheethour_timesheet_relationship',

        field_name='timesheet_uuid',
        is_list=False,
        organization=None,
    )
