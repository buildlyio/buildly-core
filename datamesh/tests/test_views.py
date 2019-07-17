import uuid

import pytest

import factories
from datamesh import views

from urllib.parse import urlencode

from workflow.tests.fixtures import org, org_admin, org_member, TEST_USER_DATA
from .fixtures import (
    document_logic_module,
    crm_logic_module,
    document_logic_module_model,
    appointment_logic_module_model,
    join_record
)


@pytest.mark.django_db()
class TestJoinRecordBase:

    session = {"jwt_organization_uuid": str(TEST_USER_DATA["organization_uuid"])}


@pytest.mark.django_db()
class TestJoinRecordListView(TestJoinRecordBase):
    def test_join_record_list_view_minimal(
        self,
        request_factory,
        org_admin,
        document_logic_module,
        crm_logic_module,
        document_logic_module_model,
        appointment_logic_module_model,
    ):
        join_records = factories.JoinRecord.create_batch(
            size=5,
            **{"organization__organization_uuid": TEST_USER_DATA["organization_uuid"]}
        )
        request = request_factory.get("")
        request.user = org_admin
        request.session = self.session
        response = views.JoinRecordViewSet.as_view({"get": "list"})(request)
        assert response.status_code == 200
        assert len(response.data) == 5
        assert set([str(jr.join_record_uuid) for jr in join_records]) == \
            set([jr['join_record_uuid'] for jr in response.data])

    def test_join_record_list_view_organization_only(
        self,
        request_factory,
        org_admin,
        document_logic_module,
        crm_logic_module,
        document_logic_module_model,
        appointment_logic_module_model,
    ):
        join_records = factories.JoinRecord.create_batch(
            size=5,
            **{"organization__organization_uuid": TEST_USER_DATA["organization_uuid"]}
        )

        factories.JoinRecord.create(organization=factories.Organization(
            name='Another Organization'
        ))

        request = request_factory.get("")
        request.user = org_admin
        request.session = self.session
        response = views.JoinRecordViewSet.as_view({"get": "list"})(request)
        assert response.status_code == 200
        assert len(response.data) == 5
        assert set([str(jr.join_record_uuid) for jr in join_records]) == set(
            [jr["join_record_uuid"] for jr in response.data]
        )

    def test_join_record_detail_fail_organization_permission(
            self, request_factory, org_admin, document_logic_module,
            crm_logic_module, document_logic_module_model, appointment_logic_module_model,):
        join_record = factories.JoinRecord.create(organization=factories.Organization(
            name='Another Organization'
        ))
        request = request_factory.get(str(join_record.join_record_uuid))
        request.user = org_admin
        request.session = self.session
        response = views.JoinRecordViewSet.as_view({"get": "list"})(request)
        assert response.status_code == 200

    def test_join_record_list_filter_one_record_id(
            self,
            request_factory,
            org_admin,
            document_logic_module,
            crm_logic_module,
            document_logic_module_model,
            appointment_logic_module_model,
    ):
        join_records = factories.JoinRecord.create_batch(
            size=5,
            **{"organization__organization_uuid": TEST_USER_DATA["organization_uuid"]}
        )
        query_params = {
            'related_record_uuid': join_records[0].related_record_uuid,
            'record_id': join_records[0].record_id,
        }
        request = request_factory.get(f'?{urlencode(query_params)}')
        request.user = org_admin
        request.session = self.session
        response = views.JoinRecordViewSet.as_view({"get": "list"})(request)
        assert response.status_code == 200
        assert len(response.data) == 1
        assert str(join_records[0].join_record_uuid) == response.data[0]["join_record_uuid"]

    def test_join_record_list_filter_several_record_uuids(
            self,
            request_factory,
            org_admin,
            document_logic_module,
            crm_logic_module,
            document_logic_module_model,
            appointment_logic_module_model,
    ):
        join_records = factories.JoinRecord.create_batch(
            size=5,
            **{"organization__organization_uuid": TEST_USER_DATA["organization_uuid"]}
        )
        query_params = {
            'related_record_uuid': f'{join_records[0].related_record_uuid},{join_records[1].related_record_uuid}',
        }
        request = request_factory.get(f'?{urlencode(query_params)}')
        request.user = org_admin
        request.session = self.session
        response = views.JoinRecordViewSet.as_view({"get": "list"})(request)
        assert response.status_code == 200
        assert len(response.data) == 2
        assert set((str(join_records[0].join_record_uuid), str(join_records[1].join_record_uuid))) == set(
            [jr["join_record_uuid"] for jr in response.data])


@pytest.mark.django_db()
class TestJoinRecordCreateView(TestJoinRecordBase):
    def test_join_record_create_view(
        self,
        request_factory,
        org_admin,
        document_logic_module,
        crm_logic_module,
        document_logic_module_model,
        appointment_logic_module_model,
    ):
        data = {
            "origin_model_name": "documentDocument",
            "related_model_name": "crmAppointment",
            "record_uuid": "322f71fe-b606-48ce-bae6-d5254479ad6f",
            "related_record_id": 7,
        }
        request = request_factory.post("", data, format="json")
        request.user = org_admin
        request.session = self.session
        response = views.JoinRecordViewSet.as_view({"post": "create"})(request)
        assert response.status_code == 201
        assert response.data["origin_model_name"] == "documentDocument"
        assert response.data["related_model_name"] == "crmAppointment"
        assert response.data["organization"] == str(TEST_USER_DATA["organization_uuid"])


@pytest.mark.django_db()
def test_join_record_detail_view(request_factory, join_record, org_admin):
    request = request_factory.get("")
    request.user = org_admin
    request.session = {"jwt_organization_uuid": str(join_record.organization.organization_uuid)}
    response = views.JoinRecordViewSet.as_view({"get": "retrieve"})(request, pk=str(join_record.pk))
    assert response.status_code == 200
    assert str(join_record.pk) == response.data["join_record_uuid"]


@pytest.mark.django_db()
def test_join_record_detail_view_no_access(request_factory, join_record, org_admin):
    request = request_factory.get("")
    request.user = org_admin
    request.session = {"jwt_organization_uuid": str(uuid.uuid4())}
    response = views.JoinRecordViewSet.as_view({"get": "retrieve"})(request, pk=str(join_record.pk))
    assert response.status_code == 404
