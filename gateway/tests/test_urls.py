from collections import OrderedDict

from django.urls import resolve
from django.test import TestCase


class URLPatternsTest(TestCase):
    def test_api_gateway_urls_with_fragment(self):
        for url in ('/crm/appointment/#some-section', '/crm/appointment#some-section'):
            match = resolve(url)
            self.assertEqual(match.url_name, 'api-gateway')
            self.assertEqual(
                OrderedDict({
                    **{'service': 'crm', 'model': 'appointment', 'pk': None, 'fragment': 'some-section'},
                    **match.kwargs,
                }),
                OrderedDict({'service': 'crm', 'model': 'appointment', 'pk': None, 'fragment': 'some-section'}),
            )

    def test_api_gateway_urls_with_int_pk(self):
        for url in (
                '/crm/appointment/653d3ea7-fc43-465d-8f36-be1678c8b7f8/',
                '/crm/appointment/653d3ea7-fc43-465d-8f36-be1678c8b7f8'
        ):
            match = resolve(url)
            self.assertEqual(match.url_name, 'api-gateway')
            self.assertEqual(
                OrderedDict({
                    **match.kwargs,
                    **{'service': 'crm', 'model': 'appointment', 'pk': '653d3ea7-fc43-465d-8f36-be1678c8b7f8'}
                }),
                OrderedDict(match.kwargs)
            )

    def test_api_gateway_urls_with_uuid_pk(self):
        match = resolve('/crm/appointment/39da9369-838e-4750-91a5-f7805cd82839/')
        self.assertEqual(match.url_name, 'api-gateway')
        self.assertEqual(
            match.kwargs,
            {
                **match.kwargs,
                **{
                    'service': 'crm',
                    'model': 'appointment',
                    'pk': '39da9369-838e-4750-91a5-f7805cd82839',
                }
            }
        )

    def test_api_gateway_urls_without_pk(self):
        match = resolve('/crm/appointment/')
        self.assertEqual(match.url_name, 'api-gateway')

        self.assertEqual(
            OrderedDict({
                **match.kwargs,
                **{'service': 'crm', 'model': 'appointment', 'pk': None}
            }),
            OrderedDict({'service': 'crm', 'model': 'appointment', 'pk': None})
        )

        match = resolve('/crm/appointment')
        self.assertEqual(match.url_name, 'api-gateway')

        self.assertEqual(
            OrderedDict({
                **match.kwargs,
                **{'service': 'crm', 'model': 'appointment', 'pk': None}
            }),
            OrderedDict({'service': 'crm', 'model': 'appointment', 'pk': None})
        )

    def test_admin_url(self):
        match = resolve('/admin/')
        self.assertEqual(match.namespace, 'admin')
        self.assertEqual(match.url_name, 'index')

    def test_docs_swagger(self):
        match = resolve('/docs/')
        self.assertEqual(match.url_name, 'schema-swagger-ui')

    def test_docs_swagger_json(self):
        match = resolve('/docs/swagger.json')
        self.assertEqual(match.url_name, 'schema-swagger-json')
