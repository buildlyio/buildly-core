import pytest

from factory import Faker

from oauth2_provider.models import Application
from rest_framework.reverse import reverse
from core.tests.fixtures import (
    auth_api_client,
    auth_superuser_api_client,
    oauth_application,
    superuser,
)


@pytest.mark.django_db()
class TestApplicationListView:
    ENDPOINT_BASE_URL = reverse('application-list')

    def test_list_application_superuser(
        self, auth_superuser_api_client, oauth_application, superuser
    ):
        """
        Superusers are able to list all the objects
        """
        response = auth_superuser_api_client.get(self.ENDPOINT_BASE_URL)
        assert response.status_code == 200
        assert len(response.data) == 1

    def test_list_application_normaluser(self, auth_api_client, oauth_application):
        """
        Normal users aren't able to list any object
        """
        response = auth_api_client.get(self.ENDPOINT_BASE_URL)
        assert response.status_code == 403


@pytest.mark.django_db()
class TestApplicationCreateView:
    ENDPOINT_BASE_URL = reverse('application-list')

    def test_create_application_superuser(self, auth_superuser_api_client, superuser):
        """
        Superusers are able to create new oauth applications
        """
        data = {
            'client_type': Application.CLIENT_PUBLIC,
            'authorization_grant_type': Application.GRANT_PASSWORD,
            'name': Faker('name').generate(),
        }

        response = auth_superuser_api_client.post(self.ENDPOINT_BASE_URL, data)
        assert response.status_code == 201
        assert response.data['name'] == data['name']

    def test_create_application_normaluser(self, auth_api_client):
        """
        Normal users aren't able to create oauth applications
        """
        data = {
            'client_type': Application.CLIENT_PUBLIC,
            'authorization_grant_type': Application.GRANT_PASSWORD,
            'name': Faker('name').generate(),
        }

        response = auth_api_client.post(self.ENDPOINT_BASE_URL, data)
        assert response.status_code == 403


@pytest.mark.django_db()
class TestApplicationRetrieveViews:
    ENDPOINT_BASE_URL = reverse('application-list')

    def test_retrieve_unexisting_application(
        self, auth_superuser_api_client, superuser
    ):
        url = f'{self.ENDPOINT_BASE_URL}1111/'

        response = auth_superuser_api_client.get(url)
        assert response.status_code == 404

    def test_retrieve_application_superuser(
        self, auth_superuser_api_client, oauth_application, superuser
    ):
        """
        Superusers are able to retrieve any oauth application
        """
        url = f'{self.ENDPOINT_BASE_URL}{oauth_application.pk}/'

        response = auth_superuser_api_client.get(url)
        assert response.status_code == 200
        assert response.data['name'] == oauth_application.name

    def test_retrieve_application_normaluser(self, auth_api_client, oauth_application):
        """
        Normal users aren't able to retrieve any oauth application
        """
        url = f'{self.ENDPOINT_BASE_URL}{oauth_application.pk}/'

        response = auth_api_client.get(url)
        assert response.status_code == 403


@pytest.mark.django_db()
class TestApplicationUpdateView:
    ENDPOINT_BASE_URL = reverse('application-list')

    def test_update_application_superuser(
        self, auth_superuser_api_client, oauth_application, superuser
    ):
        """
        Superuser is able to update oauth applications
        """
        url = f'{self.ENDPOINT_BASE_URL}{oauth_application.pk}/'

        data = {
            'client_type': Application.CLIENT_PUBLIC,
            'authorization_grant_type': Application.GRANT_PASSWORD,
            'name': Faker('name').generate(),
        }
        response = auth_superuser_api_client.put(url, data)
        assert response.status_code == 200
        assert response.data['name'] == data['name']

    def test_update_application_normaluser(self, auth_api_client, oauth_application):
        """
        Normal users aren't able to update oauth applications
        """
        url = f'{self.ENDPOINT_BASE_URL}{oauth_application.pk}/'

        data = {
            'client_type': Application.CLIENT_PUBLIC,
            'authorization_grant_type': Application.GRANT_PASSWORD,
            'name': Faker('name').generate(),
        }
        response = auth_api_client.put(url, data)
        assert response.status_code == 403


@pytest.mark.django_db()
class TestApplicationDeleteView:
    ENDPOINT_BASE_URL = reverse('application-list')

    def test_delete_unexisting_application(self, auth_superuser_api_client, superuser):
        url = f'{self.ENDPOINT_BASE_URL}999/'

        response = auth_superuser_api_client.delete(url)
        assert response.status_code == 404

    def test_delete_application_superuser(
        self, auth_superuser_api_client, oauth_application, superuser
    ):
        """
        Superusers are able to delete any oauth application
        """
        url = f'{self.ENDPOINT_BASE_URL}{oauth_application.pk}/'

        response = auth_superuser_api_client.delete(url)
        assert response.status_code == 204

        with pytest.raises(Application.DoesNotExist):
            Application.objects.get(pk=oauth_application.pk)

    def test_delete_application_normaluser(self, auth_api_client, oauth_application):
        """
        Normal users aren't able to delete oauth applications
        """
        url = f'{self.ENDPOINT_BASE_URL}{oauth_application.pk}/'

        response = auth_api_client.delete(url)
        assert response.status_code == 403
