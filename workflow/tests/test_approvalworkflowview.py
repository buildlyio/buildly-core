from django.test import TestCase
import factories
from rest_framework.test import APIRequestFactory
from rest_framework.reverse import reverse

from ..views import ApprovalWorkflowViewSet


class ApprovalWorkflowViewTest(TestCase):
    def setUp(self):
        self.user = factories.User(is_superuser=True, is_staff=True)
        self.organization = factories.Organization(id=1)
        factories.CoreUser(user=self.user, organization=self.organization)
        factory = APIRequestFactory()
        self.request = factory.post('/api/approvalworkflow/')

    def test_create_approvalworkflow(self):
        user_john = factories.User(first_name='John', last_name='Lennon')
        user_paul = factories.User(first_name='Paul', last_name='McCartney')
        assigned_user = factories.CoreUser(user=user_john,
                                           organization=self.organization)
        requested_user = factories.CoreUser(user=user_paul,
                                            organization=self.organization)
        approval_type = factories.ApprovalType()
        assigned_user_url = reverse('tolauser-detail',
                                    kwargs={'pk': assigned_user.id},
                                    request=self.request)
        requested_user_url = reverse('tolauser-detail',
                                     kwargs={'pk': requested_user.id},
                                     request=self.request)
        approval_type_url = reverse('approvaltype-detail',
                                    kwargs={'pk': approval_type.id},
                                    request=self.request)
        user_url = reverse('user-detail', kwargs={'pk': self.user.id},
                           request=self.request)

        data = {'assigned_to': assigned_user_url,
                'requested_from': requested_user_url,
                'approval_type': approval_type_url}
        self.request = APIRequestFactory().post('/api/approvalworkflow/', data)
        self.request.user = self.user
        view = ApprovalWorkflowViewSet.as_view({'post': 'create'})
        response = view(self.request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['assigned_to'], assigned_user_url)
        self.assertEqual(response.data['requested_from'], requested_user_url)
        self.assertEqual(response.data['created_by'], user_url)
