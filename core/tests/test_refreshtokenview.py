import pytest
import secrets

from oauth2_provider.models import RefreshToken
from rest_framework.reverse import reverse
from core.tests.fixtures import auth_api_client, auth_superuser_api_client, oauth_application, oauth_access_token, \
    oauth_refresh_token, superuser


@pytest.mark.django_db()
class TestRefreshTokenListView:
    ENDPOINT_BASE_URL = reverse('refreshtoken-list')

    def test_list_refreshtoken_superuser(self, auth_superuser_api_client, oauth_refresh_token, superuser):
        """
        Superusers are able to list all the objects
        """
        response = auth_superuser_api_client.get(self.ENDPOINT_BASE_URL)
        assert response.status_code == 200
        assert len(response.data) == 1

    def test_list_refreshtoken_normaluser(self, auth_api_client, oauth_refresh_token):
        """
        Normal users are not able to list any object
        """
        response = auth_api_client.get(self.ENDPOINT_BASE_URL)
        assert response.status_code == 403


@pytest.mark.django_db()
class TestRefreshTokenCreateView:
    ENDPOINT_BASE_URL = reverse('refreshtoken-list')

    def test_create_refreshtoken_superuser(self, auth_superuser_api_client, oauth_application, oauth_access_token,
                                           superuser):
        """
        Nobody is able to create new access tokens
        """
        data = {
            'token': secrets.token_urlsafe(8),
            'user': superuser,
            'application': oauth_application,
            'access_token': oauth_access_token
        }

        response = auth_superuser_api_client.post(self.ENDPOINT_BASE_URL, data)
        assert response.status_code == 405


@pytest.mark.django_db()
class TestRefreshTokenRetrieveViews:
    ENDPOINT_BASE_URL = reverse('refreshtoken-list')

    def test_retrieve_unexisting_refreshtoken(self, auth_superuser_api_client, superuser):
        url = f'{self.ENDPOINT_BASE_URL}1111/'

        response = auth_superuser_api_client.get(url)
        assert response.status_code == 404

    def test_retrieve_refreshtoken_superuser(self, auth_superuser_api_client, oauth_refresh_token, superuser):
        """
        Superusers are able to retrieve any access token
        """
        url = f'{self.ENDPOINT_BASE_URL}{oauth_refresh_token.pk}/'

        response = auth_superuser_api_client.get(url)
        assert response.status_code == 200
        assert response.data['token'] == oauth_refresh_token.token

    def test_retrieve_refreshtoken_normaluser(self, auth_api_client, oauth_refresh_token):
        """
        Normal users are not able to retrieve any access token
        """
        url = f'{self.ENDPOINT_BASE_URL}{oauth_refresh_token.pk}/'

        response = auth_api_client.get(url)
        assert response.status_code == 403


@pytest.mark.django_db()
class TestRefreshTokenUpdateView:
    ENDPOINT_BASE_URL = reverse('refreshtoken-list')

    def test_update_refreshtoken_superuser(self, auth_superuser_api_client, oauth_refresh_token, superuser):
        """
        Nobody is able to update access tokens
        """
        url = f'{self.ENDPOINT_BASE_URL}{oauth_refresh_token.pk}/'

        data = {
            'token': secrets.token_urlsafe(8)
        }
        response = auth_superuser_api_client.put(url, data)
        assert response.status_code == 405


@pytest.mark.django_db()
class TestRefreshTokenDeleteView:
    ENDPOINT_BASE_URL = reverse('refreshtoken-list')

    def test_delete_unexisting_refreshtoken(self, auth_superuser_api_client, superuser):
        url = f'{self.ENDPOINT_BASE_URL}999/'

        response = auth_superuser_api_client.delete(url)
        assert response.status_code == 404

    def test_delete_refreshtoken_superuser(self, auth_superuser_api_client, oauth_refresh_token, superuser):
        """
        Superusers are able to delete any access token
        """
        url = f'{self.ENDPOINT_BASE_URL}{oauth_refresh_token.pk}/'

        response = auth_superuser_api_client.delete(url)
        assert response.status_code == 204

        with pytest.raises(RefreshToken.DoesNotExist):
            RefreshToken.objects.get(pk=oauth_refresh_token.pk)

    def test_delete_refreshtoken_normaluser(self, auth_api_client, oauth_refresh_token):
        """
        Normal users aren't able to delete access tokens
        """
        url = f'{self.ENDPOINT_BASE_URL}{oauth_refresh_token.pk}/'

        response = auth_api_client.delete(url)
        assert response.status_code == 403


@pytest.mark.django_db()
class TestRefreshTokenFilterView:
    ENDPOINT_BASE_URL = reverse('refreshtoken-list')

    def test_filter_refreshtoken_by_user_username(self, auth_superuser_api_client, oauth_refresh_token, superuser):
        """
        Superusers can filter access tokens by users' username
        """
        query_string = f'user__username={oauth_refresh_token.user.username}'
        url = f'{self.ENDPOINT_BASE_URL}?{query_string}'

        response = auth_superuser_api_client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['token'] == oauth_refresh_token.token
