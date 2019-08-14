from datetime import date
from unittest.mock import Mock

import pytest
from django.utils.dateparse import parse_datetime

from datamesh.models import JoinRecord
from workflow.seeds.seed import SeedDataMesh, SeedEnv, SeedLogicModule
from datamesh.tests.fixtures import org, relationship


@pytest.mark.django_db()
def test_seed_data_mesh(org, relationship):
    join_record_data = [
        {
            "record_uuid": "61a012e5-d70b-4801-acb3-507b913fcd54",
            "related_record_uuid": "900498a7-8630-4c7c-9762-2447cc2178ce",
            "origin_model_name": "productsProduct",
            "related_model_name": "documentsDocument"
        },
        {
            "record_uuid": "a73ae6b9-66b2-4ae4-9f2c-d1765eb42869",
            "related_record_uuid": "551629e8-bb28-4734-a3e4-7edb239854b2",
            "origin_model_name": "productsProduct",
            "related_model_name": "documentsDocument"
        }
    ]
    pk_maps = {
        'products': {
            "61a012e5-d70b-4801-acb3-507b913fcd54": "dbfb819a-fa48-4c32-901a-4cb7ac31b1c9",
            "a73ae6b9-66b2-4ae4-9f2c-d1765eb42869": "7db2939e-05fd-480a-a375-e1d1575e5af3",
        },
        'documents': {
            "900498a7-8630-4c7c-9762-2447cc2178ce": "90ca2c17-e445-478d-9648-666daac66ffa",
            "551629e8-bb28-4734-a3e4-7edb239854b2": "a5e16b81-af04-452e-8478-d3be8ce275f4",
        }
    }
    seed_data_mesh = SeedDataMesh(join_record_data)
    seed_data_mesh.seed(pk_maps, org)
    assert 2 == JoinRecord.objects.count()
    assert 1 == JoinRecord.objects.filter(
        organization=org,
        relationship=relationship,
        record_uuid="dbfb819a-fa48-4c32-901a-4cb7ac31b1c9",
        related_record_uuid="90ca2c17-e445-478d-9648-666daac66ffa"
    ).count()
    assert 1 == JoinRecord.objects.filter(
        organization=org,
        relationship=relationship,
        record_uuid="7db2939e-05fd-480a-a375-e1d1575e5af3",
        related_record_uuid="a5e16b81-af04-452e-8478-d3be8ce275f4"
    ).count()


@pytest.mark.django_db()
def test_set_week_of_the_org_created_week(org):
    org.create_date = date(2019, 8, 14)  # wednesday in week 33
    org.save()
    test_data = [
        {
            "uuid": "878db099-b8c1-4482-b4a8-11e26168c933",
            "start_date": "2019-07-30T07:30:00+02:00",  # tuesday in week 31
            "end_date": "2019-07-31T16:00:00+02:00",
        },
        {
            "uuid": "edeb1722-5b43-4eb0-ae52-b5598e40e704",
            "start_date": "2019-08-08T07:00:00+02:00",  # thursday in week 32
        }]
    seed_env = Mock(SeedEnv)
    seed_env.organization = org
    seed_logic_module = SeedLogicModule(seed_env, {})
    seed_logic_module.set_week_of_the_org_created_week(test_data, "start_date")
    seed_logic_module.set_week_of_the_org_created_week(test_data, "end_date")
    new_start_date = parse_datetime(test_data[0]['start_date'])
    assert new_start_date.isocalendar()[1] == 33
    assert new_start_date.strftime("%A") == "Tuesday"
    assert new_start_date.hour == 7
    assert new_start_date.minute == 30
    assert new_start_date.tzname() == '+0200'
    assert test_data[0]['start_date'] == '2019-08-13T07:30:00+02:00'
    assert test_data[0]['end_date'] == '2019-08-14T16:00:00+02:00'
    assert test_data[1]['start_date'] == '2019-08-22T07:00:00+02:00'
    assert parse_datetime(test_data[1]['start_date']).isocalendar()[1] == 34


# ToDo:
# def test_seed_bifrost()
# def test_seed_logic_modules()
