from django.test import TestCase
from django.contrib.auth.models import Permission
import factories

from core.models import CoreUser


class AdminViewTest(TestCase):
    def test_admin_user_auth_page_with_superuser(self):
        """Super user should see superuser status field on django admin"""
        CoreUser.objects.create_superuser('admin', 'admin@example.com', 'Password123')
        another_user = factories.CoreUser(username='another_user')

        self.client.login(username='admin', password='Password123')

        url = '/admin/core/coreuser/{}/change/'.format(another_user.pk)
        response = self.client.get(url)
        self.assertContains(response, 'Superuser status')

    def test_admin_user_auth_page_with_staff_user(self):
        """Staff user shouldn't see superuser status field on django admin"""
        staff_user = CoreUser.objects.create_user('staff_user',
                                              'staffuser@example.com',
                                              'Password123')
        permission = Permission.objects.get(name='Can change core user')
        staff_user.user_permissions.add(permission)
        staff_user.is_staff = True
        staff_user.save()

        another_user = factories.CoreUser(username='another_user')

        self.client.login(username='staff_user', password='Password123')

        url = '/admin/core/coreuser/{}/change/'.format(another_user.pk)
        response = self.client.get(url)
        response.user = staff_user
        self.assertContains(response, 'Staff status')
        self.assertNotContains(response, 'Superuser status')

    def test_admin_user_permissions_section_with_superuser(self):
        """Super user should see user permissions section on django admin"""
        CoreUser.objects.create_superuser('admin', 'admin@example.com', 'Password123')
        another_user = factories.CoreUser(username='another_user')

        self.client.login(username='admin', password='Password123')

        url = '/admin/core/coreuser/{}/change/'.format(another_user.pk)
        response = self.client.get(url)
        self.assertContains(response, 'User permissions')

    def test_admin_user_permissions_section_with_staff_user(self):
        """Staff user shouldn't see user permissions section field on django admin"""
        staff_user = CoreUser.objects.create_user('staff_user', 'staffuser@example.com', 'Password123')
        permission = Permission.objects.get(name='Can change core user')
        staff_user.user_permissions.add(permission)
        staff_user.is_staff = True
        staff_user.save()

        another_user = factories.CoreUser(username='another_user')

        self.client.login(username='staff_user', password='Password123')

        url = '/admin/core/coreuser/{}/change/'.format(another_user.pk)
        response = self.client.get(url)
        self.assertNotContains(response, 'User permissions')
