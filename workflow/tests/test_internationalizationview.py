from django.test import TestCase
import factories
from rest_framework.test import APIRequestFactory

from workflow.models import Internationalization
from ..views import InternationalizationViewSet


class InternationalizationListViewTest(TestCase):
    def setUp(self):
        factories.Internationalization()
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()

    def test_list_internationalization_superuser(self):
        """
        Superusers are able to list all the objects
        """
        self.core_user.is_staff = True
        self.core_user.is_superuser = True
        self.core_user.save()

        request = self.factory.get('/internationalization/')
        view = InternationalizationViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_internationalization_normaluser(self):
        """
        Normal users are able to list all the objects
        """
        request = self.factory.get('/internationalization/')
        request.user = self.core_user
        view = InternationalizationViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)


class InternationalizationCreateViewTest(TestCase):
    def setUp(self):
        self.core_user = factories.CoreUser()
        self.factory = APIRequestFactory()

    def test_create_internationalization_superuser(self):
        """
        Superusers are able to create new translations
        """
        self.core_user.is_staff = True
        self.core_user.is_superuser = True
        self.core_user.save()

        data = {
            'language': 'pt-BR',
            'language_file': '{"name": "Nome", "gender": "Gênero"}',
        }
        request = self.factory.post('/internationalization/', data)
        request.user = self.core_user
        view = InternationalizationViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['language'], data['language'])

    def test_create_internationalization_normaluser(self):
        """
        Normal users aren't able to create new translations
        """
        data = {
            'language': 'pt-BR',
            'language_file': '{"name": "Nome", "gender": "Gênero"}',
        }
        request = self.factory.post('/internationalization/', data)
        request.user = self.core_user
        view = InternationalizationViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 403)


class InternationalizationRetrieveViewsTest(TestCase):
    def setUp(self):
        self.core_user = factories.CoreUser()
        self.factory = APIRequestFactory()

    def test_retrieve_unexisting_internationalization(self):
        request = self.factory.get('/internationalization/1111')
        request.user = self.core_user
        view = InternationalizationViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=1111)
        self.assertEqual(response.status_code, 404)

    def test_retrieve_internationalization_superuser(self):
        """
        Superusers are able to retrieve any translation
        """
        self.core_user.is_staff = True
        self.core_user.is_superuser = True
        self.core_user.save()
        inter = factories.Internationalization()

        request = self.factory.get('/internationalization/{}'.format(inter.id))
        request.user = self.core_user
        view = InternationalizationViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=inter.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['language'], inter.language)

    def test_retrieve_internationalization_normaluser(self):
        """
        Normal users are able to retrieve any translation
        """
        inter = factories.Internationalization()

        request = self.factory.get('/internationalization/{}'.format(inter.id))
        request.user = self.core_user
        view = InternationalizationViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=inter.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['language'], inter.language)


class InternationalizationUpdateViewTest(TestCase):
    def setUp(self):
        self.core_user = factories.CoreUser()
        self.factory = APIRequestFactory()

    def test_update_unexisting_internationalization(self):
        self.core_user.is_staff = True
        self.core_user.is_superuser = True
        self.core_user.save()

        data = {'language': 'pt-BR'}
        request = self.factory.post('/internationalization/', data)
        request.user = self.core_user
        view = InternationalizationViewSet.as_view({'post': 'update'})
        response = view(request, pk=999)

        self.assertEqual(response.status_code, 404)

    def test_update_internationalization_superuser(self):
        """
        Superusers are able to update translations
        """
        self.core_user.is_staff = True
        self.core_user.is_superuser = True
        self.core_user.save()
        inter = factories.Internationalization()

        data = {
            'language': 'pt-BR',
            'language_file': '{"name": "Nome", "gender": "Gênero"}',
        }
        request = self.factory.post('/internationalization/', data)
        request.user = self.core_user
        view = InternationalizationViewSet.as_view({'post': 'update'})
        response = view(request, pk=inter.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['language'], data['language'])

    def test_update_internationalization_normaluser(self):
        """
        Normal users aren't able to update translations
        """
        inter = factories.Internationalization()

        data = {'language': 'pt-BR'}
        request = self.factory.post('/internationalization/', data)
        request.user = self.core_user
        view = InternationalizationViewSet.as_view({'post': 'update'})
        response = view(request, pk=inter.pk)

        self.assertEqual(response.status_code, 403)


class InternationalizationDeleteViewTest(TestCase):
    def setUp(self):
        self.core_user = factories.CoreUser()
        self.factory = APIRequestFactory()

    def test_delete_unexisting_internationalization(self):
        self.core_user.is_staff = True
        self.core_user.is_superuser = True
        self.core_user.save()

        request = self.factory.delete('/internationalization/')
        request.user = self.core_user
        view = InternationalizationViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=999)

        self.assertEqual(response.status_code, 404)

    def test_delete_internationalization_superuser(self):
        """
        Superusers are able to delete any translation
        """
        self.core_user.is_staff = True
        self.core_user.is_superuser = True
        self.core_user.save()
        inter = factories.Internationalization()

        request = self.factory.delete('/internationalization/')
        request.user = self.core_user
        view = InternationalizationViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=inter.pk)

        self.assertEqual(response.status_code, 204)
        self.assertRaises(
            Internationalization.DoesNotExist,
            Internationalization.objects.get,
            pk=inter.pk,
        )

    def test_delete_internationalization_normaluser(self):
        """
        Normal users aren't able to delete translations
        """
        inter = factories.Internationalization()

        request = self.factory.delete('/internationalization/')
        request.user = self.core_user
        view = InternationalizationViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=inter.pk)

        self.assertEqual(response.status_code, 403)


class InternationalizationFilterViewTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()

    def test_filter_internationalization_by_language(self):
        """
        Any user can filter translations by language
        """
        factories.Internationalization()
        inter_pt_br = factories.Internationalization(language='pt-BR')

        query_string = 'language={}'.format(inter_pt_br.language)
        url = '/internationalization/?{}'.format(query_string)

        request = self.factory.get(url)
        request.user = self.core_user
        view = InternationalizationViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['language'], inter_pt_br.language)
