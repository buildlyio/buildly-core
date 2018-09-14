from django.test import TestCase
import factories
from django.contrib.auth.models import User, Permission


class AdminViewTest(TestCase):
    def test_admin_user_auth_page_with_superuser(self):
        """Super user should see superuser status field on django admin"""
        User.objects.create_superuser('admin', 'admin@example.com',
                                      'Password123')
        another_user = factories.User(username='another_user')

        self.client.login(username='admin', password='Password123')

        url = '/admin/auth/user/{}/change/'.format(another_user.pk)
        response = self.client.get(url)
        self.assertContains(response, 'Superuser status')

    def test_admin_user_auth_page_with_staff_user(self):
        """Staff user shouldn't see superuser status field on django admin"""
        staff_user = User.objects.create_user('staff_user',
                                              'staffuser@example.com',
                                              'Password123')
        factories.CoreUser(user=staff_user)
        permission = Permission.objects.get(name='Can change user')
        staff_user.user_permissions.add(permission)
        staff_user.is_staff = True
        staff_user.save()

        another_user = factories.User(username='another_user')

        self.client.login(username='staff_user', password='Password123')

        url = '/admin/auth/user/{}/change/'.format(another_user.pk)
        response = self.client.get(url)
        self.assertContains(response, 'Staff status')
        self.assertNotContains(response, 'Superuser status')

    def test_admin_user_permissions_section_with_superuser(self):
        """Super user should see user permissions section on django admin"""
        User.objects.create_superuser('admin', 'admin@example.com',
                                      'Password123')
        another_user = factories.User(username='another_user')

        self.client.login(username='admin', password='Password123')

        url = '/admin/auth/user/{}/change/'.format(another_user.pk)
        response = self.client.get(url)
        self.assertContains(response, 'User permissions')

    def test_admin_user_permissions_section_with_staff_user(self):
        """Staff user shouldn't see user permissions section field on
        django admin"""
        staff_user = User.objects.create_user('staff_user',
                                              'staffuser@example.com',
                                              'Password123')
        factories.CoreUser(user=staff_user)
        permission = Permission.objects.get(name='Can change user')
        staff_user.user_permissions.add(permission)
        staff_user.is_staff = True
        staff_user.save()

        another_user = factories.User(username='another_user')

        self.client.login(username='staff_user', password='Password123')

        url = '/admin/auth/user/{}/change/'.format(another_user.pk)
        response = self.client.get(url)
        self.assertNotContains(response, 'User permissions')
