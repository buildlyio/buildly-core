import pytest

import factories
from datamesh import views

from workflow.tests.fixtures import org, org_admin, org_member, TEST_USER_DATA
from .fixtures import logic_module_model


@pytest.mark.django_db()
class TestJoinRecordBase:

    session = {
        'jwt_organization_uuid': TEST_USER_DATA['organization_uuid'],
    }

    def set_up(self):
        self.logic_module1 = factories.LogicModule(
            name='document'
        )
        self.logic_module2 = factories.LogicModule(
            name='crm'
        )
        self.logic_module_model1 = factories.LogicModuleModel(
            logic_module=self.logic_module1,
            model='Document'
        )
        self.logic_module_model2 = factories.LogicModuleModel(
            logic_module=self.logic_module2,
            model='Appointment'
        )


@pytest.mark.django_db()
class TestJoinRecordCreateView(TestJoinRecordBase):

    def test_join_record_create_view(self, request_factory, org_admin):

        self.set_up()

        data = {
            "origin_model_name": "documentDocument",
            "related_model_name": "crmAppointment",
            "record_uuid": "322f71fe-b606-48ce-bae6-d5254479ad6f",
            "related_record_id": 7
        }
        request = request_factory.post('', data, format='json')
        request.user = org_admin
        request.session = self.session
        response = views.JoinRecordViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 201
        assert response.data['origin_model_name'] == 'documentDocument'
        assert response.data['related_model_name'] == 'crmAppointment'
        assert response.data['organization'] == TEST_USER_DATA['organization_uuid']
