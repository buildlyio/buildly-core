# -*- coding: utf-8 -*-
from importlib import import_module
import json
import logging
import os
import re
import sys
from urlparse import urljoin

from chargebee import InvalidRequestError
from chargebee.models import Customer, Subscription

from django.contrib import auth
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sites.models import Site
from django.core import mail
from django.core.urlresolvers import clear_url_caches
from django.http.request import HttpRequest
from django.test import Client, RequestFactory, TestCase, override_settings
from django.conf import settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
import factories
from unittest.mock import Mock, patch
from workflow.models import (Organization, CoreUser, CoreUser, ROLE_VIEW_ONLY,
                             ROLE_ORGANIZATION_ADMIN, TITLE_CHOICES)

from .. import views, DEMO_BRANCH
from ..apps import ROOT_URLCONF as ROOT_URLCONF_WEB


class IndexViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.tola_user = factories.CoreUser()

    def test_dispatch_unauthenticated(self):
        request = self.factory.get('', follow=True)
        request.user = AnonymousUser()
        response = views.IndexView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    @override_settings(TOLA_ACTIVITY_URL='https://tolaactivity.com')
    @override_settings(TOLA_TRACK_URL='https://tolatrack.com/')
    def test_dispatch_authenticated_with_urls_set(self):
        request = self.factory.get('')
        request.user = self.tola_user.user
        response = views.IndexView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['tolaactivity_url'],
                         'https://tolaactivity.com')
        self.assertEqual(response.context_data['tolatrack_url'],
                         'https://tolatrack.com/')
        template_content = response.render().content
        self.assertIn('https://tolaactivity.com', template_content)
        self.assertIn('https://tolatrack.com/', template_content)


class LoginViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def tearDown(self):
        os.environ['APP_BRANCH'] = ''

    def _reload_urlconf(self):
        clear_url_caches()
        if settings.ROOT_URLCONF in sys.modules:
            reload(sys.modules[settings.ROOT_URLCONF])
            reload(sys.modules[ROOT_URLCONF_WEB])
        return import_module(settings.ROOT_URLCONF)

    def test_org_signup_link_toladata_website(self):
        # As the url_patterns are cached when python load the module, also the
        # settings are cached there. As we want to override a setting, we need
        # to reload also the urls in order to catch the new value.
        self._reload_urlconf()
        response = self.client.get(reverse('login'), follow=True)
        template_content = response.content
        self.assertIn(
            ('Don\'t have an organization registered? Please visit our '
             'website <a href="https://www.toladata.com/">toladata.com</a> '
             'to sign up for a free trial.'),
            template_content)

    def test_org_signup_link_toladata_website_demo(self):
        os.environ['APP_BRANCH'] = DEMO_BRANCH
        self._reload_urlconf()
        response = self.client.get(reverse('login'), follow=True)
        template_content = response.content
        self.assertNotIn(
            ('Don\'t have an organization registered? Please visit our '
             'website <a href="https://www.toladata.com/">toladata.com</a> '
             'to sign up for a free trial.'),
            template_content)

    def test_with_social_auth_button_non_https(self):
        self._reload_urlconf()
        response = self.client.get(reverse('login'), follow=True)
        template_content = response.content
        self.assertIn('<div class="social-buttons row">', template_content)
        self.assertIn('<i class="icon-google"></i>', template_content)
        self.assertNotIn('<i class="icon-microsoft">', template_content)

    def test_with_social_auth_button_https(self):
        self._reload_urlconf()
        response = self.client.get(reverse('login'), follow=True,
                                   **{'wsgi.url_scheme': 'https'})
        template_content = response.content
        self.assertIn('<div class="social-buttons row">', template_content)
        self.assertIn('<i class="icon-google"></i>', template_content)
        self.assertIn('<i class="icon-microsoft">', template_content)

    def test_without_social_auth_button(self):
        os.environ['APP_BRANCH'] = DEMO_BRANCH
        self._reload_urlconf()
        response = self.client.get(reverse('login'), follow=True)
        template_content = response.content
        self.assertNotIn('<div class="social-buttons row">', template_content)
        self.assertNotIn('<i class="icon-google"></i>', template_content)
        self.assertNotIn('<i class="icon-microsoft">', template_content)

    def test_with_forgot_password_link(self):
        self._reload_urlconf()
        response = self.client.get(reverse('login'), follow=True)
        template_content = response.content
        password_reset_url = reverse('password_reset')
        self.assertIn(
            ('<a href="{}">Forgot my password</a>'.format(password_reset_url)),
            template_content)

    def test_login_unactivated_account(self):
        user = factories.User(username='John', is_active=False,)
        user.set_password('SAFEPASS1!')
        user.save()
        factories.CoreUser(user=user)
        self.client.post('/accounts/login/', {'username': user.username,
                                              'password': 'SAFEPASS1!'})
        user = auth.get_user(self.client)
        self.assertEqual(user.is_authenticated(), False)

    @override_settings(LOGIN_REDIRECT_URL='test.com')
    def test_login_activated_account(self):
        """After successful login users should be authenticated"""
        user = factories.User(username='John', is_active=True)
        user.set_password('SAFEPASS1!')
        user.save()
        factories.CoreUser(user=user)
        self.client.post('/accounts/login/', {'username': user.username,
                                              'password': 'SAFEPASS1!'})
        user = auth.get_user(self.client)
        self.assertEqual(user.is_authenticated(), True)

    def test_with_contact_support_message(self):
        self._reload_urlconf()
        response = self.client.get(reverse('login'), follow=True)
        template_content = response.content
        self.assertIn('Trouble logging in? <a href="#" data-toggle="modal" '
                      'data-target="#freshwidget-modal">Contact support</a>',
                      template_content)

    @override_settings(LOGIN_REDIRECT_URL='test.com')
    def test_login_redirect_after_success(self):
        """After successful login users should be redirected to
         Login_Redirect_url  variable"""
        user = factories.User(username='John', is_active=True)
        user.set_password('SAFEPASS1!')
        user.save()
        factories.CoreUser(user=user)
        response = self.client.post('/accounts/login/',
                                    {'username': user.username,
                                     'password': 'SAFEPASS1!'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'test.com')


class RegisterViewGetTest(TestCase):
    # Classes for testing
    class SubscriptionTest:
        def __init__(self, values):
            self.subscription = Subscription(values)
            self.subscription.status = values.get('status', 'active')

    class CustomerTest:
        def __init__(self, values):
            self.customer = Customer(values)
            self.customer.first_name = values['first_name']
            self.customer.last_name = values['last_name']
            self.customer.email = values['email']
            self.customer.company = values['company']

    def setUp(self):
        self.factory = RequestFactory()

    def test_get_with_disclaimer_in_tolasite(self):
        site = Site.objects.create(domain='api.toladata.com', name='API')
        CoreUser.objects.create(
            name='TolaData',
            privacy_disclaimer='Nice disclaimer',
            site=site)

        request = self.factory.get('')
        response = views.RegisterView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        template_content = response.content
        self.assertIn('Nice disclaimer', template_content)

    def test_get_with_disclaimer_in_template(self):
        request = self.factory.get('')
        response = views.RegisterView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        template_content = response.content
        self.assertIn('The controller is TolaData GmbH',
                      template_content)
        self.assertIn('Privacy disclaimer accepted', template_content)

    def test_get_with_org_organization_uuid(self):
        org = factories.Organization(organization_uuid='123456')

        query_params = '?organization_uuid={}'.format(org.organization_uuid)
        request = self.factory.get(
            '/accounts/register/{}'.format(query_params))
        response = views.RegisterView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        template_content = response.content
        self.assertIn(('<input type="text" name="org" value="{}" disabled '
                       'required class="textinput textInput form-control" '
                       'id="id_org" />').format(org.name), template_content)

    def test_get_with_org_invalid_organization_uuid(self):
        query_params = '?organization_uuid=1234'
        request = self.factory.get(
            '/accounts/register/{}'.format(query_params))
        response = views.RegisterView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        template_content = response.content
        self.assertIn(('<input type="text" name="org" required '
                       'class="textinput textInput form-control" '
                       'id="id_org" />'), template_content)

    @override_settings(DEFAULT_REPLY_TO='noreply@test.com')
    def test_get_with_chargebee_active_sub_in_template(self):
        sub_test = self.SubscriptionTest({})
        Subscription.retrieve = Mock(return_value=sub_test)
        customer_test = self.CustomerTest({
            'first_name': 'John',
            'last_name': 'Lennon',
            'email': 'johnlennon@test.com',
            'company': 'The Beatles'
        })
        Customer.retrieve = Mock(return_value=customer_test)

        query_params = '?cus_id={}&sub_id={}'.format('543221', '12345')
        request = self.factory.get(
            '/accounts/register/{}'.format(query_params))
        response = views.RegisterView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        template_content = response.content

        self.assertIn(
            ('<input type="text" name="first_name" value="John" '
             'id="id_first_name" class="textinput textInput '
             'form-control" maxlength="30" />'),
            template_content)
        self.assertIn(
            ('<input type="text" name="last_name" value="Lennon" '
             'id="id_last_name" class="textinput textInput '
             'form-control" maxlength="30" />'),
            template_content)
        self.assertIn(
            ('<input type="email" name="email" value="johnlennon@test.com" '
             'readonly required class="emailinput form-control"'
             ' id="id_email" />'),
            template_content)
        self.assertIn(
            ('<input type="text" name="org" value="The Beatles" disabled '
             'required class="textinput textInput form-control" '
             'id="id_org" />'),
            template_content)
        org = Organization.objects.get(name='The Beatles')
        self.assertEqual(org.chargebee_subscription_id, '12345')

    def test_get_with_chargebee_cancel_sub_in_template(self):
        sub_test = self.SubscriptionTest({'status': 'canceled'})
        Subscription.retrieve = Mock(return_value=sub_test)
        customer_test = self.CustomerTest({
            'first_name': 'John',
            'last_name': 'Lennon',
            'email': 'johnlennon@test.com',
            'company': 'The Beatles'
        })
        Customer.retrieve = Mock(return_value=customer_test)

        query_params = '?cus_id={}&sub_id={}'.format('543221', '12345')
        request = self.factory.get(
            '/accounts/register/{}'.format(query_params))
        response = views.RegisterView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertRaises(
            Organization.DoesNotExist,
            Organization.objects.get, name='The Beatles')

    def test_get_with_chargebee_demo(self):
        sub_test = self.SubscriptionTest({})
        Subscription.retrieve = Mock(return_value=sub_test)
        customer_test = self.CustomerTest({
            'first_name': 'John',
            'last_name': 'Lennon',
            'email': 'johnlennon@test.com',
            'company': 'The Beatles'
        })
        Customer.retrieve = Mock(return_value=customer_test)

        os.environ['APP_BRANCH'] = DEMO_BRANCH
        query_params = '?cus_id={}&sub_id={}'.format(
            'johnlennon@test.com', '1234567890')
        request = self.factory.get(
            '/accounts/register/{}'.format(query_params))
        response = views.RegisterView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertRaises(
            Organization.DoesNotExist,
            Organization.objects.get, name='The Beatles')
        os.environ['APP_BRANCH'] = ''

    def test_get_with_chargebee_without_sub_in_template(self):
        json_obj = {
            'message': "Sorry, we couldn't find that resource",
            'error_code': 500
        }
        external_response = InvalidRequestError(500, json_obj)
        Subscription.retrieve = Mock(return_value=external_response)
        query_params = '?cus_id={}'.format('johnlennon@test.com',)
        request = self.factory.get(
            '/accounts/register/{}'.format(query_params))
        response = views.RegisterView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertRaises(
            Organization.DoesNotExist,
            Organization.objects.get, name='The Beatles')

    def test_get_with_data_in_the_url(self):
        query_params = '?cus_fname={}&cus_lname={}&cus_email={}'.format(
            'John', 'Lennon', 'johnlennon@test.com')
        request = self.factory.get(
            '/accounts/register/{}'.format(query_params))
        response = views.RegisterView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        template_content = response.content

        self.assertIn(
            ('<input type="text" name="first_name" value="John" '
             'id="id_first_name" class="textinput textInput '
             'form-control" maxlength="30" />'),
            template_content)
        self.assertIn(
            ('<input type="text" name="last_name" value="Lennon" '
             'id="id_last_name" class="textinput textInput '
             'form-control" maxlength="30" />'),
            template_content)
        self.assertIn(
            ('<input type="email" name="email" value="johnlennon@test.com" '
             'readonly required class="emailinput form-control"'
             ' id="id_email" />'),
            template_content)
        self.assertIn(
            ('<input type="text" name="org" required class="textinput '
             'textInput form-control" id="id_org" />'),
            template_content)

    def test_get_with_data_in_the_url_cus_id(self):
        customer_test = self.CustomerTest({
            'first_name': 'John',
            'last_name': 'Lennon',
            'email': 'johnlennon@test.com',
            'company': 'The Beatles'
        })
        Customer.retrieve = Mock(return_value=customer_test)

        query_params = '?cus_id={}&cus_fname={}&cus_lname={}&cus_email={}'.\
            format('543221', 'Paul', 'McCartney', 'paulmccartney@test.com')
        request = self.factory.get(
            '/accounts/register/{}'.format(query_params))
        response = views.RegisterView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        template_content = response.content

        self.assertIn(
            ('<input type="text" name="first_name" value="John" '
             'id="id_first_name" class="textinput textInput '
             'form-control" maxlength="30" />'),
            template_content)
        self.assertIn(
            ('<input type="text" name="last_name" value="Lennon" '
             'id="id_last_name" class="textinput textInput '
             'form-control" maxlength="30" />'),
            template_content)
        self.assertIn(
            ('<input type="email" name="email" value="johnlennon@test.com" '
             'readonly required class="emailinput form-control"'
             ' id="id_email" />'),
            template_content)
        self.assertIn(
            ('<input type="text" name="org" value="The Beatles" disabled '
             'required class="textinput textInput form-control" '
             'id="id_org" />'),
            template_content)

    def test_cus_email_not_editable(self):
        '''If users coming from ChargeBee and email already filled then email
        field should not be readonly'''

        query_params = '?cus_fname={}&cus_lname={}&cus_email={}'.format(
            'John', 'Lennon', 'johnlennon@test.com')
        request = self.factory.get(
            '/accounts/register/{}'.format(query_params))
        response = views.RegisterView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        template_content = response.content
        self.assertIn(
            ('<input type="email" name="email" value="johnlennon@test.com" '
             'readonly required class="emailinput form-control"'
             ' id="id_email" />'),
            template_content)

    def test_get_with_encrypted_email_data(self):

        org = factories.Organization(organization_uuid='123456')
        email = 'bobdylan@test.com'
        encrypted_email = urlsafe_base64_encode(
            force_bytes(email)).decode()

        query_params = '?organization_uuid={}&amp;email={}'.format(
            org.organization_uuid, encrypted_email)
        request = self.factory.get(
            '/accounts/register/{}'.format(query_params))

        response = views.RegisterView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        template_content = response.content

        self.assertIn(
            ('<input type="email" name="email" value="bobdylan@test.com" '
             'readonly required class="emailinput form-control"'
             ' id="id_email" />'),
            template_content)

        self.assertIn(('<input type="text" name="org" value="{}" disabled '
                       'required class="textinput textInput form-control" '
                       'id="id_org" />').format(org.name), template_content)


class RegisterViewPostTest(TestCase):
    # Classes for testing
    class SubscriptionTest:
        def __init__(self, values):
            self.subscription = Subscription(values)
            self.subscription.status = values.get('status', 'active')

    class CustomerTest:
        def __init__(self, values):
            self.customer = Customer(values)
            self.customer.email = values['email']
            self.customer.company = values['company']

    def setUp(self):
        self.factory = RequestFactory()
        self.organization = factories.Organization(organization_uuid='12345')
        factories.Group(name=ROLE_VIEW_ONLY)
        logging.disable(logging.ERROR)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    @staticmethod
    def _hotfix_django_bug(request):
        # Django 1.4 bug
        # https://code.djangoproject.com/ticket/17971
        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

    def test_post_organization_not_found(self):
        data = {
            'org': 'Invalid Org'
        }
        request = self.factory.post(reverse('register'), data)
        self._hotfix_django_bug(request)
        view = views.RegisterView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        template_content = response.content
        self.assertIn('The Organization was not found',
                      template_content)

    def test_post_fields_not_sent(self):
        data = {
            'org': self.organization.name
        }
        request = self.factory.post(reverse('register'), data)
        self._hotfix_django_bug(request)
        view = views.RegisterView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        template_content = response.content
        for field in ('username', 'password1', 'password2', 'email',
                      'privacy_disclaimer_accepted'):
            msg = ('<p id="error_1_id_{}" class="help-block"><strong>'
                   'This field is required.</strong></p>'.format(field))
            self.assertIn(msg, template_content)

    @patch('tola.track_sync.requests')
    def test_post_success_with_full_name(self, mock_requests):
        mock_requests.post.return_value = Mock(status_code=201)

        data = {
            'first_name': 'John',
            'last_name': 'Lennon',
            'email': 'johnlennon@test.com',
            'username': 'ILoveYoko',
            'password1': 'SAFEPASS1!',
            'password2': 'SAFEPASS1!',
            'title': TITLE_CHOICES[0][0],
            'privacy_disclaimer_accepted': 'on',
            'org': self.organization.name,
        }
        request = self.factory.post(reverse('register'), data)
        self._hotfix_django_bug(request)
        view = views.RegisterView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(reverse('login'), response.url)

        tolauser = CoreUser.objects.select_related('user').get(
            name='John Lennon')
        user = tolauser.user
        self.assertEqual(user.first_name, data['first_name'])
        self.assertEqual(user.last_name, data['last_name'])
        self.assertEqual(user.email, data['email'])
        self.assertEqual(tolauser.organization, self.organization)
        self.assertEqual(tolauser.title, data['title'])
        self.assertTrue(User.objects.filter(username='ILoveYoko').exists())

    @override_settings(TOLA_TRACK_SYNC_ENABLED=True)
    @patch('tola.track_sync.requests')
    def test_post_success_syncing_track(self, mock_requests):
        mock_requests.post.return_value = Mock(status_code=201)
        data = {
            'first_name': 'John',
            'last_name': 'Lennon',
            'email': 'johnlennon@test.com',
            'username': 'ILoveYoko',
            'password1': 'SAFEPASS1!',
            'password2': 'SAFEPASS1!',
            'title': TITLE_CHOICES[0][0],
            'privacy_disclaimer_accepted': 'on',
            'org': self.organization.name,
        }
        request = self.factory.post(reverse('register'), data)
        self._hotfix_django_bug(request)
        view = views.RegisterView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(reverse('login'), response.url)
        self.assertTrue(mock_requests.post.called)

    @patch('tola.track_sync.requests')
    def test_post_success_with_first_name(self, mock_requests):
        mock_requests.post.return_value = Mock(status_code=201)

        data = {
            'first_name': 'John',
            'email': 'johnlennon@test.com',
            'username': 'ILoveYoko',
            'password1': 'SAFEPASS1!',
            'password2': 'SAFEPASS1!',
            'title': TITLE_CHOICES[0][0],
            'privacy_disclaimer_accepted': 'on',
            'org': self.organization.name,
        }
        request = self.factory.post(reverse('register'), data)
        self._hotfix_django_bug(request)
        view = views.RegisterView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(reverse('login'), response.url)

        tolauser = CoreUser.objects.select_related('user').get(
            name='John')
        user = tolauser.user
        self.assertEqual(user.first_name, data['first_name'])
        self.assertEqual(user.email, data['email'])
        self.assertEqual(tolauser.organization, self.organization)
        self.assertEqual(tolauser.title, data['title'])
        self.assertTrue(User.objects.filter(username='ILoveYoko').exists())

    @patch('tola.track_sync.requests')
    def test_post_success_user_is_org_admin(self, mock_requests):
        mock_requests.post.return_value = Mock(status_code=201)
        sub_test = self.SubscriptionTest({})
        Subscription.retrieve = Mock(return_value=sub_test)
        customer_test = self.CustomerTest({
            'email': 'johnlennon@test.com',
            'company': self.organization.name
        })
        Customer.retrieve = Mock(return_value=customer_test)
        factories.Group(name=ROLE_ORGANIZATION_ADMIN)

        data = {
            'first_name': 'John',
            'email': 'johnlennon@test.com',
            'username': 'ILoveYoko',
            'password1': 'SAFEPASS1!',
            'password2': 'SAFEPASS1!',
            'title': TITLE_CHOICES[0][0],
            'privacy_disclaimer_accepted': 'on',
        }
        query_params = '?cus_id={}'.format('1234567890')
        request = self.factory.post('/accounts/register/{}'.format(
            query_params), data)
        self._hotfix_django_bug(request)
        view = views.RegisterView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(reverse('login'), response.url)

        tolauser = CoreUser.objects.select_related('user').get(
            name='John')
        user = tolauser.user
        self.assertEqual(user.first_name, data['first_name'])
        self.assertEqual(user.email, data['email'])

        user_groups = user.groups.all().values_list('name', flat=True)
        self.assertIn(ROLE_ORGANIZATION_ADMIN, user_groups)

    @patch('tola.track_sync.requests')
    def test_post_success_with_default_org(self, mock_requests):
        mock_requests.post.return_value = Mock(status_code=201)
        factories.Organization(name=settings.DEFAULT_ORG)
        os.environ['APP_BRANCH'] = DEMO_BRANCH

        data = {
            'first_name': 'John',
            'last_name': 'Lennon',
            'email': 'johnlennon@test.com',
            'username': 'ILoveYoko',
            'password1': 'SAFEPASS1!',
            'password2': 'SAFEPASS1!',
            'title': TITLE_CHOICES[0][0],
            'privacy_disclaimer_accepted': 'on',
        }
        request = self.factory.post(reverse('register'), data)
        self._hotfix_django_bug(request)
        view = views.RegisterView.as_view()
        response = view(request)
        os.environ['APP_BRANCH'] = ''
        self.assertEqual(response.status_code, 302)
        self.assertEqual(reverse('login'), response.url)

        tolauser = CoreUser.objects.select_related('user').get(
            name='John Lennon')
        user = tolauser.user
        self.assertEqual(user.first_name, data['first_name'])
        self.assertEqual(user.last_name, data['last_name'])
        self.assertEqual(user.email, data['email'])
        self.assertEqual(tolauser.organization.name, settings.DEFAULT_ORG)
        self.assertEqual(tolauser.title, data['title'])
        self.assertTrue(User.objects.filter(username='ILoveYoko').exists())

        os.environ['APP_BRANCH'] = ''

    @patch('tola.track_sync.requests')
    def test_post_success_with_organization_uuid(self, mock_requests):
        mock_requests.post.return_value = Mock(status_code=201)

        data = {
            'first_name': 'John',
            'email': 'johnlennon@test.com',
            'username': 'ILoveYoko',
            'password1': 'SAFEPASS1!',
            'password2': 'SAFEPASS1!',
            'title': TITLE_CHOICES[0][0],
            'privacy_disclaimer_accepted': 'on',
        }
        query_params = '?organization_uuid={}'.format(
            self.organization.organization_uuid)
        url = '/accounts/register/{}'.format(query_params)
        request = self.factory.post(url, data)
        self._hotfix_django_bug(request)
        view = views.RegisterView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(reverse('login'), response.url)

        tolauser = CoreUser.objects.select_related('user').get(
            name='John')
        user = tolauser.user
        self.assertEqual(user.first_name, data['first_name'])
        self.assertEqual(user.email, data['email'])
        self.assertEqual(tolauser.organization, self.organization)
        self.assertEqual(tolauser.title, data['title'])
        self.assertTrue(User.objects.filter(username='ILoveYoko').exists())

    def test_post_unique_email(self):
        factories.User(email='johnlennon@test.com')

        data = {
            'first_name': 'John',
            'last_name': 'Lennon',
            'email': 'johnlennon@test.com',
            'username': 'ILoveYoko',
            'password1': 'SAFEPASS1!',
            'password2': 'SAFEPASS1!',
            'title': TITLE_CHOICES[0][0],
            'privacy_disclaimer_accepted': 'on',
            'org': self.organization.name,
        }
        request = self.factory.post(reverse('register'), data)
        self._hotfix_django_bug(request)
        view = views.RegisterView.as_view()
        response = view(request)
        template_content = response.content

        match = '<p id="error_1_id_email" class="help-block">' \
                '<strong>Email address is already used.</strong></p>'
        self.assertIn(match, template_content)

    @patch('tola.track_sync.requests')
    @patch('web.views.load_strategy')
    def test_post_success_with_partial_pipeline(self, mock_load_strategy,
                                                mock_requests):
        class PartialTest(object):
            def __init__(self, backend):
                self.backend = backend

        class StrategyTest(object):
            def __init__(self, partial):
                self.partial = partial

            def partial_load(self, *args):
                return self.partial

        partial = PartialTest('blablabla')
        strategy = StrategyTest(partial)
        mock_load_strategy.return_value = strategy
        mock_requests.post.return_value = Mock(status_code=201)

        data = {
            'first_name': 'John',
            'email': 'johnlennon@test.com',
            'username': 'ILoveYoko',
            'password1': 'SAFEPASS1!',
            'password2': 'SAFEPASS1!',
            'title': TITLE_CHOICES[0][0],
            'privacy_disclaimer_accepted': 'on',
        }
        query_params = '?organization_uuid={}&partial_token=09876'.format(
            self.organization.organization_uuid)
        url = '/accounts/register/{}'.format(query_params)
        request = self.factory.post(url, data)
        self._hotfix_django_bug(request)
        view = views.RegisterView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(reverse('social:complete', args=('blablabla',)),
                         response.url)

        tolauser = CoreUser.objects.select_related('user').get(
            name='John')
        user = tolauser.user
        self.assertEqual(user.first_name, data['first_name'])
        self.assertEqual(user.email, data['email'])
        self.assertEqual(tolauser.organization, self.organization)
        self.assertEqual(tolauser.title, data['title'])

        self.assertTrue(User.objects.filter(username='ILoveYoko').exists())

    def test_save_chargebee_subscription_no_org(self):
        sub_test = self.SubscriptionTest({})
        Subscription.retrieve = Mock(return_value=sub_test)
        customer_test = self.CustomerTest({
            'email': 'johnlennon@test.com',
            'company': 'New Org'
        })
        Customer.retrieve = Mock(return_value=customer_test)

        params = {
            'sub_id': '12345',
        }
        view = views.RegisterView()
        result = view._save_chargebee_subscription(params)
        self.assertIsNotNone(result)

        org = Organization.objects.get(name='New Org')
        self.assertEqual(org.chargebee_subscription_id, '12345')

    def test_save_chargebee_subscription_with_org(self):
        org = factories.Organization(
            name='ChargeBee Org', chargebee_subscription_id='dfs908ewrh23')

        sub_test = self.SubscriptionTest({})
        Subscription.retrieve = Mock(return_value=sub_test)
        customer_test = self.CustomerTest({
            'email': 'johnlennon@test.com',
            'company': org.name
        })
        Customer.retrieve = Mock(return_value=customer_test)

        params = {
            'sub_id': '12345',
        }
        view = views.RegisterView()
        result = view._save_chargebee_subscription(params)
        self.assertIsNotNone(result)

        org = Organization.objects.get(pk=org.pk)
        self.assertEqual(org.chargebee_subscription_id, '12345')

    def test_save_chargebee_subscription_no_valid_sub_id(self):
        json_obj = {
            'message': "Sorry, we couldn't find that resource",
            'error_code': 500
        }
        sub_test = InvalidRequestError(500, json_obj)
        Subscription.retrieve = Mock(side_effect=sub_test)
        customer_test = self.CustomerTest({
            'email': 'johnlennon@test.com',
            'company': 'New Org'
        })
        Customer.retrieve = Mock(return_value=customer_test)

        params = {
            'sub_id': '12345',
        }
        view = views.RegisterView()
        view._save_chargebee_subscription(params)
        self.assertRaises(
            Organization.DoesNotExist,
            Organization.objects.get, name='New Org')

    @patch('tola.track_sync.requests')
    def test_post_common_password(self, mock_requests):
        mock_requests.post.return_value = Mock(status_code=201)

        data = {
            'email': 'johnlennon@test.com',
            'username': 'ILoveYoko',
            'password1': 'password',
            'password2': 'password',
            'title': TITLE_CHOICES[0][0],
            'privacy_disclaimer_accepted': 'on',
            'org': self.organization.name,
        }
        request = self.factory.post(reverse('register'), data)
        self._hotfix_django_bug(request)
        view = views.RegisterView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This password is too common.")

    @patch('tola.track_sync.requests')
    def test_post_short_password(self, mock_requests):
        mock_requests.post.return_value = Mock(status_code=201)

        data = {
            'email': 'johnlennon@test.com',
            'username': 'ILoveYoko',
            'password1': 'pass1',
            'password2': 'pass1',
            'title': TITLE_CHOICES[0][0],
            'privacy_disclaimer_accepted': 'on',
            'org': self.organization.name,
        }
        request = self.factory.post(reverse('register'), data)
        self._hotfix_django_bug(request)
        view = views.RegisterView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This password is too short. It must "
                                      "contain at least 6 characters.")

    @patch('tola.track_sync.requests')
    def test_post_numeric_password(self, mock_requests):
        mock_requests.post.return_value = Mock(status_code=201)

        data = {
            'email': 'johnlennon@test.com',
            'username': 'ILoveYoko',
            'password1': '001122',
            'password2': '001122',
            'title': TITLE_CHOICES[0][0],
            'privacy_disclaimer_accepted': 'on',
            'org': self.organization.name,
        }
        request = self.factory.post(reverse('register'), data)
        self._hotfix_django_bug(request)
        view = views.RegisterView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This password is entirely numeric.")

    @patch('tola.track_sync.requests')
    def test_post_password_multiple_validators(self, mock_requests):
        mock_requests.post.return_value = Mock(status_code=201)

        data = {
            'email': 'johnlennon@test.com',
            'username': 'ILoveYoko',
            'password1': '1234',
            'password2': '1234',
            'title': TITLE_CHOICES[0][0],
            'privacy_disclaimer_accepted': 'on',
            'org': self.organization.name,
        }
        request = self.factory.post(reverse('register'), data)
        self._hotfix_django_bug(request)
        view = views.RegisterView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This password is too common.")
        self.assertContains(response, "This password is too short. It must "
                                      "contain at least 6 characters.")
        self.assertContains(response, "This password is entirely numeric.")


class TolaTrackSiloProxyTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.tola_user = factories.CoreUser()

    def test_get_unauthenticated_user(self):
        request = self.factory.get('')
        view = views.TolaTrackSiloProxy.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 403)

    @override_settings(TOLA_TRACK_URL='https://tolatrack.com')
    @override_settings(TOLA_TRACK_TOKEN='TheToken')
    @patch('web.views.requests')
    def test_get_authenticated_user_url_without_ending_slash(
            self, mock_requests):
        external_response = ['foo', {'bar': 'baz'}]
        mock_requests.get.return_value = Mock(
            status_code=200, content=json.dumps(external_response))
        request = Mock(user=self.tola_user.user)
        response = views.TolaTrackSiloProxy().get(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), external_response)
        mock_requests.get.assert_called_once_with(
            'https://tolatrack.com/api/silo?user_uuid={}'.format(
                self.tola_user.tola_user_uuid),
            headers={'content-type': 'application/json',
                     'Authorization': 'Token TheToken'})

    @override_settings(TOLA_TRACK_URL='https://tolatrack.com/')
    @override_settings(TOLA_TRACK_TOKEN='TheToken')
    @patch('web.views.requests')
    def test_get_authenticated_user_url_with_ending_slash(
            self, mock_requests):
        external_response = ['foo', {'bar': 'baz'}]
        mock_requests.get.return_value = Mock(
            status_code=200, content=json.dumps(external_response))
        request = Mock(user=self.tola_user.user)
        response = views.TolaTrackSiloProxy().get(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), external_response)
        mock_requests.get.assert_called_once_with(
            'https://tolatrack.com/api/silo?user_uuid={}'.format(
                self.tola_user.tola_user_uuid),
            headers={'content-type': 'application/json',
                     'Authorization': 'Token TheToken'})

    @override_settings(TOLA_TRACK_URL='https://tolatrack.com/')
    @override_settings(TOLA_TRACK_TOKEN='TheToken')
    @patch('web.views.requests')
    def test_get_gateway_502_exception(
            self, mock_requests):
        mock_requests.get.return_value = Mock(status_code=400)
        request = Mock(user=self.tola_user.user)
        response = views.TolaTrackSiloProxy().get(request)
        self.assertEqual(response.status_code, 502)


class TolaTrackSiloDataProxyTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_get_unauthenticated_user(self):
        request = self.factory.get('')
        view = views.TolaTrackSiloDataProxy.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 403)

    @override_settings(TOLA_TRACK_URL='https://tolatrack.com')
    @override_settings(TOLA_TRACK_TOKEN='TheToken')
    @patch('web.views.requests')
    def test_get_authenticated_user_url_without_ending_slash(
            self, mock_requests):
        external_response = ['foo', {'bar': 'baz'}]
        mock_requests.get.return_value = Mock(
            status_code=200, content=json.dumps(external_response))
        request = HttpRequest()
        response = views.TolaTrackSiloDataProxy().get(request, '123')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), external_response)
        mock_requests.get.assert_called_once_with(
            'https://tolatrack.com/api/silo/123/data',
            headers={'content-type': 'application/json',
                     'Authorization': 'Token TheToken'})

    @override_settings(TOLA_TRACK_URL='https://tolatrack.com/')
    @override_settings(TOLA_TRACK_TOKEN='TheToken')
    @patch('web.views.requests')
    def test_get_authenticated_user_url_with_ending_slash(
            self, mock_requests):
        external_response = ['foo', {'bar': 'baz'}]
        mock_requests.get.return_value = Mock(
            status_code=200, content=json.dumps(external_response))
        request = HttpRequest()
        response = views.TolaTrackSiloDataProxy().get(request, '123')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), external_response)
        mock_requests.get.assert_called_once_with(
            'https://tolatrack.com/api/silo/123/data',
            headers={'content-type': 'application/json',
                     'Authorization': 'Token TheToken'})

    @override_settings(TOLA_TRACK_URL='https://tolatrack.com/')
    @override_settings(TOLA_TRACK_TOKEN='TheToken')
    @patch('web.views.requests')
    def test_get_authenticated_user_url_with_query(
            self, mock_requests):
        external_response = ['foo', {'bar': 'baz'}]
        mock_requests.get.return_value = Mock(
            status_code=200, content=json.dumps(external_response))
        request = HttpRequest()
        request.method = 'GET'
        request.GET.update({'query': '{"status":"open"}'})
        response = views.TolaTrackSiloDataProxy().get(request, '123')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), external_response)
        mock_requests.get.assert_called_once_with(
            'https://tolatrack.com/api/silo/123/data?query={"status":"open"}',
            headers={'content-type': 'application/json',
                     'Authorization': 'Token TheToken'})

    @override_settings(TOLA_TRACK_URL='https://tolatrack.com/')
    @override_settings(TOLA_TRACK_TOKEN='TheToken')
    @patch('web.views.requests')
    def test_get_authenticated_user_url_with_query_group(
            self, mock_requests):
        external_response = ['foo', {'bar': 'baz'}]
        mock_requests.get.return_value = Mock(
            status_code=200, content=json.dumps(external_response))
        request = HttpRequest()
        request.method = 'GET'
        request.GET.update({
            'query': '{"_id":null}',
            'group': '{"$sum":[1]}'
        })
        response = views.TolaTrackSiloDataProxy().get(request, '123')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), external_response)
        mock_requests.get.assert_called_once_with(
            'https://tolatrack.com/api/silo/123/data?query={"_id":null}'
            '&group={"$sum":[1]}',
            headers={'content-type': 'application/json',
                     'Authorization': 'Token TheToken'})

    @override_settings(TOLA_TRACK_URL='https://tolatrack.com/')
    @override_settings(TOLA_TRACK_TOKEN='TheToken')
    @patch('web.views.requests')
    def test_get_gateway_502_exception(
            self, mock_requests):
        mock_requests.get.return_value = Mock(status_code=400)
        request = HttpRequest()
        response = views.TolaTrackSiloDataProxy().get(request, '288')
        self.assertEqual(response.status_code, 502)


class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = factories.User()
        self.user.set_password(12345)
        self.user.save()
        self.tola_user = factories.CoreUser(user=self.user)
        self.factory = RequestFactory()

    @override_settings(LOGIN_REDIRECT_URL='https://test.com/')
    @override_settings(TOLA_TRACK_URL='https://tolatrack.com/')
    def test_logout_redirect_to_track(self):
        c = Client()
        c.post('/accounts/login/', {'username': self.user.username,
                                    'password': '12345'})
        self.user = auth.get_user(c)
        self.assertEqual(self.user.is_authenticated(), True)

        response = c.post('/accounts/logout/')
        self.user = auth.get_user(c)
        self.assertEqual(self.user.is_authenticated(), False)
        self.assertEqual(response.status_code, 302)

        url_subpath = 'accounts/logout/'
        redirect_url = urljoin(settings.TOLA_TRACK_URL, url_subpath)
        self.assertEqual(response.url, redirect_url)

    def test_logout_redirect_to_index(self):
        c = Client()
        response = c.post('/accounts/logout/')
        self.user = auth.get_user(c)
        self.assertEqual(self.user.is_authenticated(), False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')


class HealtCheckViewTest(TestCase):
    def test_health_check_success(self):
        c = Client()
        response = c.get('/health_check/')
        self.assertEqual(response.status_code, 200)


class TolaPasswordResetViewTest(TestCase):
    def setUp(self):
        self.user = factories.User()
        self.user.set_password(12345)
        self.user.save()
        self.tola_user = factories.CoreUser(user=self.user)
        self.factory = RequestFactory()

    def test_get_reset_password_form(self):
        response = self.client.get('/accounts/password_reset/')

        self.assertIn('Forgot password', response.rendered_content)
        self.assertIn('Just give us your e-mail address and we\'ll send '
                      'you an e-mail with a link to reset your password.',
                      response.rendered_content)

    def test_get_reset_password_email(self):
        data = {'email': self.user.email}

        response = self.client.post('/accounts/password_reset/',
                                    data=data, follow=True)

        self.assertIn('Email sent!', response.rendered_content)
        self.assertIn('We\'ve emailed you instructions for resetting your '
                      'password.\n      You should receive them shortly.',
                      response.rendered_content)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('TolaData Login Assistance', mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, [self.user.email])

        self.assertIn('http://testserver/accounts/reset/',
                      mail.outbox[0].body)
        self.assertIn('Dear {}'.format(self.tola_user), mail.outbox[0].body)

        self.assertIn('http://testserver/accounts/reset/',
                      mail.outbox[0].alternatives[0][0])
        self.assertIn('Dear {}'.format(self.tola_user),
                      mail.outbox[0].alternatives[0][0])


class TolaPasswordResetConfirmViewTest(TestCase):
    def setUp(self):
        self.user = factories.User()
        self.user.set_password(12345)
        self.user.save()
        self.tola_user = factories.CoreUser(user=self.user)
        self.factory = RequestFactory()

    def test_reset_the_password_success(self):
        data = {'email': self.user.email}
        new_password = {
            'new_password1': 'SAFEPASS!',
            'new_password2': 'SAFEPASS!'
        }

        self.client.post('/accounts/password_reset/', data=data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('TolaData Login Assistance', mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertIn('accounts/reset/', mail.outbox[0].body)

        match = re.search('/accounts/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/'
                          '(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
                          mail.outbox[0].body)
        reset_url = match.group(0)
        set_password_url = '/accounts/reset/{}/set-password/'.format(
            match.group(1))

        response = self.client.get(reset_url)

        self.assertRedirects(response, set_password_url)

        response = self.client.post(set_password_url,
                                    new_password, follow=True)
        self.assertIn('Your password has been set.', response.rendered_content)

        self.client.login(username=self.user.username, password='SAFEPASS!')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('You have successfuly logged in to TolaData.',
                      response.rendered_content)

    def test_reset_the_password_invalid_link(self):
        data = {'email': self.user.email}
        new_password = {
            'new_password1': 'SAFEPASS!',
            'new_password2': 'SAFEPASS!'
        }

        self.client.post('/accounts/password_reset/', data=data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('TolaData Login Assistance', mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertIn('accounts/reset/', mail.outbox[0].body)

        match = re.search('/accounts/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/'
                          '(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
                          mail.outbox[0].body)
        reset_url = match.group(0)
        set_password_url = '/accounts/reset/{}/set-password/'.format(
            match.group(1))

        response = self.client.get(reset_url)

        self.assertRedirects(response, set_password_url)

        self.client.post(set_password_url, new_password, follow=True)
        response = self.client.post(set_password_url,
                                    new_password, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid password reset link', response.rendered_content)
        self.assertIn('The password reset link was invalid, possibly because '
                      'it has already been used.', response.rendered_content)
        self.assertIn('Please request a new password reset.',
                      response.rendered_content)

        self.assertIn('<a href="/accounts/password_reset/">Reset password</a>',
                      response.rendered_content)
        self.assertIn('<a href="/accounts/login/">Cancel</a>',
                      response.rendered_content)


class TolaPasswordResetDoneViewTest(TestCase):
    def test_password_reset_done_view(self):
        response = self.client.get('/accounts/password_reset/done/')
        self.assertIn('If you do not receive a '
                      'password reset email within 10 minutes, please\n      '
                      'check your spam folder. If you still do not have it, '
                      'please verify that\n      you have entered correctly'
                      ' the email address you registered with.',
                      response.rendered_content)
