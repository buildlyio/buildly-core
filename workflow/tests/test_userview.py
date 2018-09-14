from django.test import TestCase
import factories
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory

from ..views import UserViewSet
from workflow.models import ROLE_ORGANIZATION_ADMIN


class TolaUserCreateViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_create_tolauser_disabled(self):
        request = self.factory.post('', {})
        view = UserViewSet.as_view({'post': 'create'})
        self.assertRaises(AttributeError, view, request)


class TolaUserUpdateViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = factories.User()
        self.tola_user = factories.CoreUser(user=self.user)

    def test_update_active_status_with_super_user(self):
        """ superuser can update active status of user. """
        super_user = User.objects.create_superuser('admin',
                                                   'admin@example.com',
                                                   'Password123')
        factories.CoreUser(user=super_user,
                           organization=self.tola_user.organization)

        test_user = factories.User(username='another user')
        factories.CoreUser(user=test_user,
                           organization=self.tola_user.organization)
        self.assertEqual(test_user.is_active, True)

        data = {'is_active': False}
        request = self.factory.post('', data)
        request.user = super_user
        view = UserViewSet.as_view({'post': 'update'})
        response = view(request, pk=test_user.pk)
        self.assertEqual(response.data['is_active'], False)

    def test_update_active_status_with_org_admin(self):
        """ org admins can update active status of users. """
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.tola_user.user.groups.add(group_org_admin)

        test_user = factories.User(username='another user')
        factories.CoreUser(user=test_user,
                           organization=self.tola_user.organization)
        self.assertEqual(test_user.is_active, True)

        data = {'is_active': False}
        request = self.factory.post('', data)
        request.user = self.tola_user.user
        view = UserViewSet.as_view({'post': 'update'})
        response = view(request, pk=test_user.pk)
        self.assertEqual(response.data['is_active'], False)

    def test_update_active_status_with_different_org_admin(self):
        """ org admins from another organizations
         can not update active status of users. """
        another_admin = factories.User(username='another_admin')
        another_org = factories.Organization(name='another_org')
        factories.CoreUser(user=another_admin,
                           organization=another_org)

        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        another_admin.groups.add(group_org_admin)

        test_user = factories.User(username='another user')
        factories.CoreUser(user=test_user,
                           organization=self.tola_user.organization)
        self.assertEqual(test_user.is_active, True)

        data = {'is_active': False}
        request = self.factory.post('', data)
        request.user = another_admin
        view = UserViewSet.as_view({'post': 'update'})
        response = view(request, pk=test_user.pk)
        self.assertEqual(response.status_code, 403)

    def test_update_active_status_with_view_only(self):
        """ normal user can not update active status of users. """
        test_user = factories.User(username='another user')
        factories.CoreUser(user=test_user,
                           organization=self.tola_user.organization)
        self.assertEqual(test_user.is_active, True)

        data = {'is_active': False}
        request = self.factory.post('', data)
        request.user = self.tola_user.user
        view = UserViewSet.as_view({'post': 'update'})
        response = view(request, pk=test_user.pk)
        self.assertEqual(response.status_code, 403)

    def test_update_other_fields(self):
        """ users(even org admins and superuser) can not update
        other fields of users except active status. """
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.tola_user.user.groups.add(group_org_admin)

        test_user = factories.User(username='bobmarley',
                                   first_name='Bob',
                                   last_name='Marley',
                                   email='bob@example.com',
                                   is_staff=False)
        factories.CoreUser(user=test_user,
                           organization=self.tola_user.organization)
        self.assertEqual(test_user.is_active, True)

        data = {"username": "jrneymar", "first_name": "jr.",
                "last_name": "Neymar", "email": "neymar@example.com",
                "is_staff": True}

        request = self.factory.post('', data)
        request.user = self.tola_user.user
        view = UserViewSet.as_view({'post': 'update'})
        response = view(request, pk=test_user.pk)
        self.assertEqual(response.data['username'], 'bobmarley')
        self.assertEqual(response.data['first_name'], 'Bob')
        self.assertEqual(response.data['last_name'], 'Marley')
        self.assertEqual(response.data['email'], 'bob@example.com')
        self.assertEqual(response.data['is_staff'], False)
