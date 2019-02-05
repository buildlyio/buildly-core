# -*- coding: utf-8 -*-
import imp
import logging
import urllib

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.test import TestCase, Client
from unittest.mock import Mock, patch

import factories
from web import auth_pipeline


class OAuthTest(TestCase):
    """
    Test cases for OAuth Provider interface
    """
    # Fake classes for testing
    class BackendTest(object):
        def __init__(self):
            self.WHITELISTED_EMAILS = []
            self.WHITELISTED_DOMAINS = []

        def setting(self, name, default=None):
            return self.__dict__.get(name, default)

    class CurrentPartialTest(object):
        def __init__(self, token):
            self.token = token

    def setUp(self):
        logging.disable(logging.WARNING)
        self.tola_user = factories.CoreUser()
        self.org = factories.Organization(organization_uuid='12345')
        self.country = factories.Country()
        self.site = factories.CoreUser(site=get_current_site(None),
                                        whitelisted_domains='testenv.com')
        self.app = factories.Application(user=self.tola_user.user)
        self.grant = factories.Grant(application=self.app,
                                     user=self.tola_user.user)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_authorization(self):
        """
        Tests if the simple search responds
        :return:
        """
        self.tola_user.user.set_password('1234')
        self.tola_user.user.save()

        c = Client(HTTP_USER_AGENT='Test/1.0')
        c.login(username=self.tola_user.user.username, password='1234')

        # Get Authorization token
        authorize_url = '/oauth/authorize?state=random_state_string' \
                        '&client_id={}&response_type=code'.format(
                            self.app.client_id)

        response = c.get(authorize_url, follow=True)
        self.assertContains(
            response, "value=\"CXGVOGFnTAt5cQW6m5AxbGrRq1lzKNSrou31dWm9\"")
        self.assertEqual(response.status_code, 200)

    def test_auth_allowed_in_whitelist(self):
        factories.Organization(name=settings.DEFAULT_ORG)
        backend = self.BackendTest()
        details = {'email': self.tola_user.user.email}
        result = auth_pipeline.auth_allowed(backend, details, None)
        self.assertIsNone(result)
        self.assertIn('organization_uuid', details)

    def test_auth_allowed_not_in_whitelist(self):
        factories.Organization(name=settings.DEFAULT_ORG)
        backend = self.BackendTest()
        details = {'email': self.tola_user.user.email}
        self.site.whitelisted_domains = 'anotherdomain.com'
        self.site.save()
        response = auth_pipeline.auth_allowed(backend, details, None)
        template_content = response.content
        self.assertIn("You don't appear to have permissions to access "
                      "the system.", template_content)
        self.assertIn("Please check with your organization to have access.",
                      template_content)

    def test_auth_allowed_in_oauth_domain(self):
        self.site.whitelisted_domains = None
        self.site.save()
        self.org.oauth_domains = ['testenv.com']
        self.org.save()

        backend = self.BackendTest()
        details = {'email': self.tola_user.user.email}
        result = auth_pipeline.auth_allowed(backend, details, None)
        self.assertIsNone(result)
        self.assertIn('organization_uuid', details)

    def test_auth_allowed_in_whitelisted_domains_conf(self):
        factories.Organization(name=settings.DEFAULT_ORG)
        self.site.whitelisted_domains = None
        self.site.save()

        backend = self.BackendTest()
        backend.WHITELISTED_DOMAINS = ['testenv.com']
        details = {'email': self.tola_user.user.email}
        result = auth_pipeline.auth_allowed(backend, details, None)
        self.assertIsNone(result)
        self.assertIn('organization_uuid', details)

    def test_auth_allowed_multi_oauth_domain(self):
        self.site.whitelisted_domains = None
        self.site.save()
        self.org.oauth_domains = ['testenv.com']
        self.org.save()
        factories.Organization(organization_uuid='6789', name='Another Org',
                               oauth_domains=['testenv.com'])

        backend = self.BackendTest()
        details = {'email': self.tola_user.user.email}
        response = auth_pipeline.auth_allowed(backend, details, None)
        template_content = response.content
        self.assertIn("You don't appear to have permissions to access "
                      "the system.", template_content)
        self.assertIn("Please check with your organization to have access.",
                      template_content)

    def test_auth_allowed_no_whitelist_oauth_domain(self):
        self.site.whitelisted_domains = None
        self.site.save()

        backend = self.BackendTest()
        details = {'email': self.tola_user.user.email}
        response = auth_pipeline.auth_allowed(backend, details, None)
        template_content = response.content
        self.assertIn("You don't appear to have permissions to access "
                      "the system.", template_content)
        self.assertIn("Please check with your organization to have access.",
                      template_content)

    def test_auth_allowed_no_email(self):
        factories.Organization(name=settings.DEFAULT_ORG)
        backend = self.BackendTest()
        details = {}
        response = auth_pipeline.auth_allowed(backend, details, None)
        template_content = response.content
        self.assertIn("You don't appear to have permissions to access "
                      "the system.", template_content)
        self.assertIn("Please check with your organization to have access.",
                      template_content)

    def test_check_user_does_not_exist(self):
        def kill_patches():
            patch.stopall()
            imp.reload(auth_pipeline)

        self.addCleanup(kill_patches)
        patch('social_core.pipeline.partial.partial', lambda x: x).start()
        imp.reload(auth_pipeline)

        # Create the parameters for the check_user function
        mocked = Mock()
        c_partial = self.CurrentPartialTest('09876')
        details = {
            'first_name': u'Jóhn',
            'last_name': u'Leñón',
            'email': u'johnlennón@test.com',
            'organization_uuid': self.org.organization_uuid,
        }
        kwargs = {
            'current_partial': c_partial
        }
        response = auth_pipeline.check_user(mocked, details, mocked, None,
                                            mocked, **kwargs)

        # Create redirect URL to validate
        query_params = {
            'cus_fname': details['first_name'].encode('utf8'),
            'cus_lname': details['last_name'].encode('utf8'),
            'cus_email': details['email'].encode('utf8'),
            'organization_uuid': details['organization_uuid'],
            'partial_token': c_partial.token
        }
        qp = urllib.urlencode(query_params)
        redirect_url = '/accounts/register/?{}'.format(qp)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.get('location'), redirect_url)

    def test_check_user_is_new(self):
        def kill_patches():
            patch.stopall()
            imp.reload(auth_pipeline)

        self.addCleanup(kill_patches)
        patch('social_core.pipeline.partial.partial', lambda x: x).start()
        imp.reload(auth_pipeline)

        # Create the parameters for the check_user function
        mocked = Mock()
        details = {
            'first_name': u'Jóhn',
            'last_name': u'Leñón',
            'email': u'johnlennón@test.com',
        }
        user = factories.User(first_name=details['first_name'],
                              last_name=details['last_name'],
                              email=details['email'])
        result = auth_pipeline.check_user(mocked, details, mocked, None,
                                          mocked, mocked)
        self.assertTrue(result['is_new'])
        self.assertEqual(result['user'], user)

    def test_check_user_is_not_new(self):
        def kill_patches():
            patch.stopall()
            imp.reload(auth_pipeline)

        self.addCleanup(kill_patches)
        patch('social_core.pipeline.partial.partial', lambda x: x).start()
        imp.reload(auth_pipeline)

        # Create the parameters for the check_user function
        mocked = Mock()
        details = {
            'first_name': u'Jóhn',
            'last_name': u'Leñón',
            'email': u'johnlennón@test.com',
        }
        user = factories.User(first_name=details['first_name'],
                              last_name=details['last_name'],
                              email=details['email'])
        result = auth_pipeline.check_user(mocked, details, mocked, user,
                                          mocked, mocked)
        self.assertFalse(result['is_new'])
