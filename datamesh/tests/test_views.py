import uuid
from urllib.parse import urlencode

import pytest
from rest_framework.reverse import reverse

import factories
from datamesh import views
from core.tests.fixtures import org, org_admin, org_member, TEST_USER_DATA
from .fixtures import (
    document_logic_module,
    crm_logic_module,
    document_logic_module_model,
    appointment_logic_module_model,
    join_record,
    relationship,
    relationship2
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


@pytest.mark.django_db()
class TestLogicModuleModelView:

    expected_keys = {
            'logic_module_model_uuid',
            'logic_module_endpoint_name',
            'model',
            'endpoint',
            'lookup_field_name',
            'is_local',
        }

    def test_list_logic_module_models(self,
                                      request_factory,
                                      document_logic_module_model,
                                      appointment_logic_module_model):
        request = request_factory.get(reverse('logicmodulemodel-list'))
        user = factories.CoreUser()
        request.user = user
        response = views.LogicModuleModelViewSet.as_view({"get": "list"})(request)
        assert response.status_code == 200
        assert len(response.data) == 2
        assert self.expected_keys == set(response.data[0].keys())

    def test_create_logic_module_model(self, request_factory):
        data = {
            "logic_module_endpoint_name": "location",
            "model": "siteprofile",
            "endpoint": "/siteprofiles/",
            "lookup_field_name": "uuid"
        }
        request = request_factory.post(reverse('logicmodulemodel-list'), data)
        user = factories.CoreUser(is_superuser=True)
        request.user = user
        response = views.LogicModuleModelViewSet.as_view({"post": "create"})(request)
        assert response.status_code == 201
        assert self.expected_keys == set(response.data.keys())

    def test_create_logic_module_model_no_access(self, request_factory):
        data = {
            "logic_module_endpoint_name": "location",
            "model": "siteprofile",
            "endpoint": "/siteprofiles/",
            "lookup_field_name": "uuid"
        }
        request = request_factory.post(reverse('logicmodulemodel-list'), data)

        user = factories.CoreUser()
        request.user = user
        response = views.LogicModuleModelViewSet.as_view({"post": "create"})(request)
        assert response.status_code == 403

    def test_detail_logic_module_models(self, request_factory, document_logic_module_model):
        pk = str(document_logic_module_model.pk)
        request = request_factory.get(reverse('logicmodulemodel-detail', args=(pk,)))
        user = factories.CoreUser()
        request.user = user
        response = views.LogicModuleModelViewSet.as_view({"get": "retrieve"})(request, pk=pk)
        assert response.status_code == 200
        assert self.expected_keys == set(response.data.keys())

    def test_update_logic_module_model(self, request_factory, document_logic_module_model):
        pk = str(document_logic_module_model.pk)
        data = {
            "logic_module_endpoint_name": "document",
            "model": "document",
            "endpoint": "/documents/",
            "lookup_field_name": "another_lookup_field"
        }
        request = request_factory.put(reverse('logicmodulemodel-detail', args=(pk,)), data)
        user = factories.CoreUser(is_superuser=True)
        request.user = user
        response = views.LogicModuleModelViewSet.as_view({"put": "update"})(request, pk=pk)
        assert response.status_code == 200
        assert self.expected_keys == set(response.data.keys())
        assert response.data['lookup_field_name'] == 'another_lookup_field'

    def test_update_logic_module_model_no_access(self, request_factory, document_logic_module_model):
        pk = str(document_logic_module_model.pk)
        data = {
            "logic_module_endpoint_name": "document",
            "model": "document",
            "endpoint": "/documents/",
            "lookup_field_name": "another_lookup_field"
        }
        request = request_factory.put(reverse('logicmodulemodel-detail', args=(pk,)), data)
        user = factories.CoreUser()
        request.user = user
        response = views.LogicModuleModelViewSet.as_view({"put": "update"})(request, pk=pk)
        assert response.status_code == 403

    def test_patch_logic_module_model(self, request_factory, document_logic_module_model):
        pk = str(document_logic_module_model.pk)
        data = {
            "lookup_field_name": "another_lookup_field"
        }
        request = request_factory.patch(reverse('logicmodulemodel-detail', args=(pk,)), data)
        user = factories.CoreUser(is_superuser=True)
        request.user = user
        response = views.LogicModuleModelViewSet.as_view({"patch": "partial_update"})(request, pk=pk)
        assert response.status_code == 200
        assert self.expected_keys == set(response.data.keys())
        assert response.data['lookup_field_name'] == 'another_lookup_field'

    def test_delete_logic_module_models(self, request_factory, document_logic_module_model):
        pk = str(document_logic_module_model.pk)
        request = request_factory.delete(reverse('logicmodulemodel-detail', args=(pk,)))
        user = factories.CoreUser(is_superuser=True)
        request.user = user
        response = views.LogicModuleModelViewSet.as_view({"delete": "destroy"})(request, pk=pk)
        assert response.status_code == 204

    def test_delete_logic_module_models_no_access(self, request_factory, document_logic_module_model):
        pk = str(document_logic_module_model.pk)
        request = request_factory.delete(reverse('logicmodulemodel-detail', args=(pk,)))
        user = factories.CoreUser()
        request.user = user
        response = views.LogicModuleModelViewSet.as_view({"delete": "destroy"})(request, pk=pk)
        assert response.status_code == 403


@pytest.mark.django_db()
class TestRelationshipView:

    expected_keys = {
            'relationship_uuid',
            'origin_model',
            'related_model',
            'key',
            'origin_lookup_field_name',
            'origin_fk_field_name',
            'related_lookup_field_name',
            'related_fk_field_name'
        }

    def test_list_relationships(self, request_factory, relationship, relationship2):
        request = request_factory.get(reverse('relationship-list'))
        user = factories.CoreUser()
        request.user = user
        response = views.RelationshiplViewSet.as_view({"get": "list"})(request)
        assert response.status_code == 200
        assert len(response.data) == 2
        assert set(response.data[0].keys()) == self.expected_keys
        assert set(response.data[0]['origin_model'].keys()) == TestLogicModuleModelView.expected_keys
        assert set(response.data[0]['related_model'].keys()) == TestLogicModuleModelView.expected_keys

    def test_create_relationship(self,
                                       request_factory,
                                       document_logic_module_model,
                                       appointment_logic_module_model):
        data= {
            "origin_model_id": document_logic_module_model.pk,
            "related_model_id": appointment_logic_module_model.pk,
            "key": "document_appointment_rel"
        }
        request = request_factory.post(reverse('relationship-list'), data)
        user = factories.CoreUser(is_superuser=True)
        request.user = user
        response = views.RelationshiplViewSet.as_view({"post": "create"})(request)
        assert response.status_code == 201
        assert self.expected_keys == set(response.data.keys())

    def test_create_relationship_no_access(self,
                                       request_factory,
                                       document_logic_module_model,
                                       appointment_logic_module_model):
        data= {
            "origin_model_id": document_logic_module_model.pk,
            "related_model_id": appointment_logic_module_model.pk,
            "key": "document_appointment_rel"
        }
        request = request_factory.post(reverse('relationship-list'), data)
        user = factories.CoreUser()
        request.user = user
        response = views.RelationshiplViewSet.as_view({"post": "create"})(request)
        assert response.status_code == 403

    def test_detail_relationship(self, request_factory, relationship):
        pk = str(relationship.pk)
        request = request_factory.get(reverse('relationship-detail', args=(pk,)))
        user = factories.CoreUser()
        request.user = user
        response = views.RelationshiplViewSet.as_view({"get": "retrieve"})(request, pk=pk)
        assert response.status_code == 200
        assert self.expected_keys == set(response.data.keys())

    def test_update_relationship(self, request_factory, relationship):
        pk = str(relationship.pk)
        data = {
            "origin_model_id": relationship.origin_model.pk,
            "related_model_id": relationship.related_model.pk,
            "key": "another_key_for_this_rel"
        }
        request = request_factory.put(reverse('relationship-detail', args=(pk,)), data)
        user = factories.CoreUser(is_superuser=True)
        request.user = user
        response = views.RelationshiplViewSet.as_view({"put": "update"})(request, pk=pk)
        assert response.status_code == 200
        assert self.expected_keys == set(response.data.keys())
        assert response.data['key'] == 'another_key_for_this_rel'

    def test_update_relationship_no_access(self, request_factory, relationship):
        pk = str(relationship.pk)
        data = {
            "origin_model_id": relationship.origin_model.pk,
            "related_model_id": relationship.related_model.pk,
            "key": "another_key_for_this_rel"
        }
        request = request_factory.put(reverse('relationship-detail', args=(pk,)), data)
        user = factories.CoreUser()
        request.user = user
        response = views.RelationshiplViewSet.as_view({"put": "update"})(request, pk=pk)
        assert response.status_code == 403

    def test_patch_relationship(self, request_factory, relationship):
        pk = str(relationship.pk)
        data = {
            "key": "another_key_for_this_rel"
        }
        request = request_factory.patch(reverse('relationship-detail', args=(pk,)), data)
        user = factories.CoreUser(is_superuser=True)
        request.user = user
        response = views.RelationshiplViewSet.as_view({"patch": "partial_update"})(request, pk=pk)
        assert response.status_code == 200
        assert self.expected_keys == set(response.data.keys())
        assert response.data['key'] == 'another_key_for_this_rel'

    def test_delete_relationship(self, request_factory, relationship):
        pk = str(relationship.pk)
        request = request_factory.delete(reverse('relationship-detail', args=(pk,)))
        user = factories.CoreUser(is_superuser=True)
        request.user = user
        response = views.RelationshiplViewSet.as_view({"delete": "destroy"})(request, pk=pk)
        assert response.status_code == 204

    def test_delete_relationship_no_access(self, request_factory, relationship):
        pk = str(relationship.pk)
        request = request_factory.delete(reverse('relationship-detail', args=(pk,)))
        user = factories.CoreUser()
        request.user = user
        response = views.RelationshiplViewSet.as_view({"delete": "destroy"})(request, pk=pk)
        assert response.status_code == 403
