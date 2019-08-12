import pytest

from datamesh.models import JoinRecord
from workflow.seeds.seed import SeedDataMesh
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

# ToDo:
# def test_seed_bifrost()
# def test_seed_logic_modules()
