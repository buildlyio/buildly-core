import factories
from core.models import Partner
from django.test import TestCase, Client
from rest_framework import status
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from django.urls import reverse
from core.views import PartnerViewSet

client = Client()


class GetAllPartnerTest(TestCase):
    """ Test module for GET all events API """

    def setUp(self):
        self.partner = Partner.objects.create(

        )
        self.factory = APIRequestFactory()
        self.request = self.factory.get('/')
        self.serializer_context = {
            'request': Request(self.request),
        }

    def test_list_all_partner(self):
        self.request.user = factories.CoreUser(is_superuser=True, is_staff=True)
        view = PartnerViewSet.as_view({'get': 'list'})
        response = view(self.request)
        self.assertEqual(response.status_code, 200)


class GetSinglePartnerTest(TestCase):
    """ Test module for GET single partner API """

    def setUp(self):
        self.partner = Partner.objects.create(
            name='partner name'
        )
        self.factory = APIRequestFactory()
        self.request = self.factory.get('/partner/')
        self.serializer_context = {
            'request': Request(self.request),
        }

    def test_get_valid_single_partner(self):
        self.request.user = factories.CoreUser(is_superuser=True, is_staff=True)
        view = PartnerViewSet.as_view({'get': 'retrieve'})
        response = view(self.request, pk=self.partner.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_single_partner(self):
        self.request.user = factories.CoreUser(is_superuser=True, is_staff=True)
        view = PartnerViewSet.as_view({'get': 'retrieve'})
        response = view(self.request, pk=12)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CreatePartnerTest(TestCase):
    """ Test module for inserting a new partner"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.request = self.factory.get('/partner/')
        self.valid_payload = {"name": "partner name"}

    def test_create_valid_partner(self):
        data = {'name': 'partner name', }
        request = self.factory.post(reverse('partner-list'), data, format='json')
        request.user = factories.CoreUser(is_superuser=True, is_staff=True)
        response = PartnerViewSet.as_view({'post': 'create'})(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class UpdatePartnerTest(TestCase):
    """Test module for updating an existing partner record"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.request = self.factory.get('/partner/')

    def test_valid_update_partner(self):
        self.partner = Partner.objects.create(name='partner name')
        data = {'name': 'partner name', }
        request = self.factory.put(reverse('partner-detail', args=(self.partner.pk,)), data)
        request.user = factories.CoreUser(is_superuser=True, is_staff=True)
        response = PartnerViewSet.as_view({'put': 'update'})(request, pk=self.partner.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DeleteSinglePartnerTest(TestCase):
    """ Test module for deleting an existing partner record """

    def setUp(self):
        self.factory = APIRequestFactory()
        self.request = self.factory.get('/partner/')
        self.partner = Partner.objects.create(name='test name')

    def test_valid_delete_partner(self):
        request = self.factory.delete(reverse('partner-detail', args=(self.partner.pk,)))
        request.user = factories.CoreUser(is_superuser=True, is_staff=True)
        response = PartnerViewSet.as_view({'delete': 'destroy'})(request, pk=self.partner.pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_invalid_delete_partner(self):
        request = self.factory.delete(reverse('partner-detail', args=(self.partner.pk,)))
        request.user = factories.CoreUser(is_superuser=True, is_staff=True)
        response = PartnerViewSet.as_view({'delete': 'destroy'})(request, pk=12)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
