from django.test import TestCase
import factories
from rest_framework.test import APIRequestFactory

from ..views import GroupViewSet


class GroupViewsTest(TestCase):
    def setUp(self):
        factories.Group()
        factory = APIRequestFactory()
        self.request_get = factory.get('/api/groups/')
        self.request_post = factory.post('/api/groups/')

    def test_list_groups_superuser(self):
        self.request_get.user = factories.User.build(is_superuser=True, is_staff=True)
        view = GroupViewSet.as_view({'get': 'list'})
        response = view(self.request_get)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_groups_normaluser(self):
        self.request_get.user = factories.CoreUser()
        view = GroupViewSet.as_view({'get': 'list'})
        response = view(self.request_get)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_create_group_error(self):
        # create group via POST request
        data = {'name': 'TestGroup'}
        self.request_post = APIRequestFactory().post('/api/stakeholder/', data)
        self.request_post.user = factories.User.build(is_superuser=False, is_staff=False)
        view = GroupViewSet.as_view({'post': 'create'})

        with self.assertRaises(AttributeError) as context:
            view(self.request_post)
            self.assertTrue('\'GroupViewSet\' object has no attribute '
                            '\'create\'' in context.exception)
