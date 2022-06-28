import asyncio

import pytest
from django.forms.models import model_to_dict

import factories
from core.tests.fixtures import org
from datamesh.tests.fixtures import (
    relationship,
    relationship2,
    relationship_with_10_records,
    relationship_with_local,
)
from datamesh.services import DataMesh


@pytest.mark.django_db()
class TestSyncDataMesh:
    def test_join_data_one_obj_w_relationships(self, relationship):
        factories.JoinRecord(
            relationship=relationship,
            record_id=1,
            related_record_id=2,
            record_uuid=None,
            related_record_uuid=None,
        )

        logic_module_model = relationship.origin_model
        data = {'id': 1, 'name': 'test', 'contact_uuid': 1}

        # mock client for related logic module
        class ClientMock:
            def request(self, **kwargs):
                return {'id': 1, 'file': '/somewhere/128/'}

        client_map = {
            relationship.related_model.logic_module_endpoint_name: ClientMock()
        }

        datamesh = DataMesh(
            logic_module_endpoint=logic_module_model.logic_module_endpoint_name,
            model_endpoint=logic_module_model.endpoint,
        )
        datamesh.extend_data(data, client_map)

        # validate result
        expected_data = {
            'id': 1,
            'name': 'test',
            'contact_uuid': 1,
            relationship.key: [{'id': 1, 'file': '/somewhere/128/'}],
        }

        assert data == expected_data

    def test_join_data_one_obj_w_two_relationships(
        self, relationship, relationship2, org
    ):
        factories.JoinRecord(
            relationship=relationship,
            record_id=1,
            related_record_id=2,
            record_uuid=None,
            related_record_uuid=None,
        )
        factories.JoinRecord(
            relationship=relationship2,
            record_id=1,
            related_record_id=10,
            record_uuid=None,
            related_record_uuid=None,
        )

        logic_module_model = relationship.origin_model
        data = {'id': 1, 'name': 'test', 'contact_uuid': 1}

        # mock client for related services
        class ClientMock:
            def request(self, **kwargs):
                if kwargs['model'] == 'documents':
                    return {'id': 2, 'file': '/documents/128/'}
                if kwargs['model'] == 'siteprofile':
                    return {'id': 10, 'city': 'New York'}
                return {}

        client_map = {
            relationship.related_model.logic_module_endpoint_name: ClientMock(),
            relationship2.related_model.logic_module_endpoint_name: ClientMock(),
        }

        datamesh = DataMesh(
            logic_module_endpoint=logic_module_model.logic_module_endpoint_name,
            model_endpoint=logic_module_model.endpoint,
        )
        datamesh.extend_data(data, client_map)

        # validate result
        expected_data = {
            'id': 1,
            'name': 'test',
            'contact_uuid': 1,
            relationship.key: [{'id': 2, 'file': '/documents/128/'}],
            relationship2.key: [{'id': 10, 'city': 'New York'}],
        }

        assert data == expected_data

    def test_join_data_list(self, relationship_with_10_records):
        join_records = relationship_with_10_records.joinrecords.all()

        logic_module_model = relationship_with_10_records.origin_model

        data = [
            {'uuid': str(item.record_uuid), 'name': f'Boiler #{i}'}
            for i, item in enumerate(join_records)
        ]

        # mock client for related logic module
        mocked_response_data = {
            str(item.related_record_uuid): '/documents/128/' for item in join_records
        }

        class ClientMock:
            def request(self, **kwargs):
                return {
                    'uuid': kwargs['pk'],
                    'file': mocked_response_data[kwargs['pk']],
                }

        client_map = {
            relationship_with_10_records.related_model.logic_module_endpoint_name: ClientMock()
        }

        datamesh = DataMesh(
            logic_module_endpoint=logic_module_model.logic_module_endpoint_name,
            model_endpoint=logic_module_model.endpoint,
        )
        datamesh.extend_data(data, client_map)

        for i, item in enumerate(data):
            assert item['uuid'] == str(join_records[i].record_uuid)
            assert relationship_with_10_records.key in item
            nested = item[relationship_with_10_records.key]
            assert len(nested) == 1
            assert nested[0]['uuid'] == str(join_records[i].related_record_uuid)

    def test_relationship_with_local_lm(self, relationship_with_local, org):
        factories.JoinRecord(
            relationship=relationship_with_local,
            record_id=1,
            related_record_uuid=org.organization_uuid,
            record_uuid=None,
            related_record_id=None,
        )

        logic_module_model = relationship_with_local.origin_model
        data = {'id': 1, 'name': 'test', 'contact_uuid': 1}

        datamesh = DataMesh(
            logic_module_endpoint=logic_module_model.logic_module_endpoint_name,
            model_endpoint=logic_module_model.endpoint,
        )
        datamesh.extend_data(data, {})

        # validate result
        expected_data = {
            'id': 1,
            'name': 'test',
            'contact_uuid': 1,
            relationship_with_local.key: [model_to_dict(org)],
        }

        assert data == expected_data


@pytest.mark.django_db()
class TestAsyncDataMesh:
    def test_join_data_one_obj_w_relationships(self, relationship):
        factories.JoinRecord(
            relationship=relationship,
            record_id=1,
            related_record_id=2,
            record_uuid=None,
            related_record_uuid=None,
        )

        logic_module_model = relationship.origin_model
        data = {'id': 1, 'name': 'test', 'contact_uuid': 1}

        # mock client for related logic module
        class ClientMock:
            async def request(self, **kwargs):
                return {'id': 1, 'file': '/somewhere/128/'}

        client_map = {
            relationship.related_model.logic_module_endpoint_name: ClientMock()
        }

        datamesh = DataMesh(
            logic_module_endpoint=logic_module_model.logic_module_endpoint_name,
            model_endpoint=logic_module_model.endpoint,
        )

        asyncio.run(datamesh.async_extend_data(data, client_map))

        # validate result
        expected_data = {
            'id': 1,
            'name': 'test',
            'contact_uuid': 1,
            relationship.key: [{'id': 1, 'file': '/somewhere/128/'}],
        }

        assert data == expected_data

    def test_join_data_one_obj_w_two_relationships(
        self, relationship, relationship2, org
    ):
        factories.JoinRecord(
            relationship=relationship,
            record_id=1,
            related_record_id=2,
            record_uuid=None,
            related_record_uuid=None,
        )
        factories.JoinRecord(
            relationship=relationship2,
            record_id=1,
            related_record_id=10,
            record_uuid=None,
            related_record_uuid=None,
        )

        logic_module_model = relationship.origin_model
        data = {'id': 1, 'name': 'test', 'contact_uuid': 1}

        # mock client for related services
        class ClientMock:
            async def request(self, **kwargs):
                if kwargs['model'] == 'documents':
                    return {'id': 2, 'file': '/documents/128/'}
                if kwargs['model'] == 'siteprofile':
                    return {'id': 10, 'city': 'New York'}
                return {}

        client_map = {
            relationship.related_model.logic_module_endpoint_name: ClientMock(),
            relationship2.related_model.logic_module_endpoint_name: ClientMock(),
        }

        datamesh = DataMesh(
            logic_module_endpoint=logic_module_model.logic_module_endpoint_name,
            model_endpoint=logic_module_model.endpoint,
        )
        asyncio.run(datamesh.async_extend_data(data, client_map))

        # validate result
        expected_data = {
            'id': 1,
            'name': 'test',
            'contact_uuid': 1,
            relationship.key: [{'id': 2, 'file': '/documents/128/'}],
            relationship2.key: [{'id': 10, 'city': 'New York'}],
        }

        assert data == expected_data

    def test_join_data_list(self, relationship_with_10_records):
        join_records = relationship_with_10_records.joinrecords.all()

        logic_module_model = relationship_with_10_records.origin_model

        data = [
            {'uuid': str(item.record_uuid), 'name': f'Boiler #{i}'}
            for i, item in enumerate(join_records)
        ]

        # mock client for related logic module
        mocked_response_data = {
            str(item.related_record_uuid): '/documents/128/' for item in join_records
        }

        class ClientMock:
            async def request(self, **kwargs):
                return {
                    'uuid': kwargs['pk'],
                    'file': mocked_response_data[kwargs['pk']],
                }

        client_map = {
            relationship_with_10_records.related_model.logic_module_endpoint_name: ClientMock()
        }

        datamesh = DataMesh(
            logic_module_endpoint=logic_module_model.logic_module_endpoint_name,
            model_endpoint=logic_module_model.endpoint,
        )
        asyncio.run(datamesh.async_extend_data(data, client_map))

        for i, item in enumerate(data):
            assert item['uuid'] == str(join_records[i].record_uuid)
            assert relationship_with_10_records.key in item
            nested = item[relationship_with_10_records.key]
            assert len(nested) == 1
            assert nested[0]['uuid'] == str(join_records[i].related_record_uuid)

    def test_relationship_with_local_lm(self, relationship_with_local, org):
        factories.JoinRecord(
            relationship=relationship_with_local,
            record_id=1,
            related_record_uuid=org.organization_uuid,
            record_uuid=None,
            related_record_id=None,
        )

        logic_module_model = relationship_with_local.origin_model
        data = {'id': 1, 'name': 'test', 'contact_uuid': 1}

        datamesh = DataMesh(
            logic_module_endpoint=logic_module_model.logic_module_endpoint_name,
            model_endpoint=logic_module_model.endpoint,
        )
        asyncio.run(datamesh.async_extend_data(data, {}))

        # validate result
        expected_data = {
            'id': 1,
            'name': 'test',
            'contact_uuid': 1,
            relationship_with_local.key: [model_to_dict(org)],
        }

        assert data == expected_data
