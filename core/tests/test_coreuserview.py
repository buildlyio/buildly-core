from datetime import date, timedelta
from urllib.parse import urljoin
from unittest import mock

import pytest
from django.core import mail
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.reverse import reverse

import factories
from core.models import CoreUser, EmailTemplate, Organization, TEMPLATE_RESET_PASSWORD
from core.views import CoreUserViewSet
from core.jwt_utils import create_invitation_token
from core.tests.fixtures import org, org_admin, org_member, reset_password_request, TEST_USER_DATA


@pytest.mark.django_db()
def test_coreuser_views_permissions_unauth(request_factory):
    # has no permission
    request = request_factory.get(reverse('coreuser-list'))
    response = CoreUserViewSet.as_view({'get': 'list'})(request)
    assert response.status_code == 403

    # has permission but need to send data
    request = request_factory.post(reverse('coreuser-list'))
    response = CoreUserViewSet.as_view({'post': 'create'})(request)
    assert response.status_code == 400

    # has no permission
    request = request_factory.post(reverse('coreuser-invite'))
    response = CoreUserViewSet.as_view({'post': 'invite'})(request)
    assert response.status_code == 403

    # not authorized (without token parameter)
    request = request_factory.get(reverse('coreuser-invite-check'))
    response = CoreUserViewSet.as_view({'get': 'invite_check'})(request)
    assert response.status_code == 401

    # has no permission
    request = request_factory.get(reverse('coreuser-detail', args=(1,)))
    response = CoreUserViewSet.as_view({'get': 'retrieve'})(request, pk=1)
    assert response.status_code == 403

    # has no permission
    request = request_factory.put(reverse('coreuser-detail', args=(1,)))
    response = CoreUserViewSet.as_view({'put': 'update'})(request, pk=1)
    assert response.status_code == 403

    # has no permission
    request = request_factory.patch(reverse('coreuser-detail', args=(1,)))
    response = CoreUserViewSet.as_view({'patch': 'partial_update'})(request,
                                                                    pk=1)
    assert response.status_code == 403


@pytest.mark.django_db()
def test_coreuser_views_permissions_org_member(request_factory, org_member):
    pk = org_member.pk

    # has permission
    request = request_factory.get(reverse('coreuser-list'))
    request.user = org_member
    response = CoreUserViewSet.as_view({'get': 'list'})(request)
    assert response.status_code == 200

    # has no permission
    request = request_factory.post(reverse('coreuser-invite'))
    request.user = org_member
    response = CoreUserViewSet.as_view({'post': 'invite'})(request)
    assert response.status_code == 403

    # has permission
    request = request_factory.get(reverse('coreuser-detail', args=(pk,)))
    request.user = org_member
    response = CoreUserViewSet.as_view({'get': 'retrieve'})(request, pk=pk)
    assert response.status_code == 200

    # has no permission
    request = request_factory.put(reverse('coreuser-detail', args=(pk,)))
    request.user = org_member
    response = CoreUserViewSet.as_view({'put': 'update'})(request, pk=pk)
    assert response.status_code == 403

    # has no permission
    request = request_factory.patch(reverse('coreuser-detail', args=(1,)))
    request.user = org_member
    response = CoreUserViewSet.as_view({'patch': 'partial_update'})(request,
                                                                    pk=1)
    assert response.status_code == 403


@pytest.mark.django_db()
class TestCoreUserCreate:

    def test_registration_fail(self, request_factory):
        # check that 'password' and 'organization_name' fields are required
        for field_name in ['password', 'organization_name']:
            data = TEST_USER_DATA.copy()
            data.pop(field_name)
            request = request_factory.post(reverse('coreuser-list'), data)
            response = CoreUserViewSet.as_view({'post': 'create'})(request)
            assert response.status_code == 400

    def test_registration_of_first_org_user(self, request_factory):
        request = request_factory.post(reverse('coreuser-list'), TEST_USER_DATA)
        response = CoreUserViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 201

        user = CoreUser.objects.get(username=TEST_USER_DATA['username'])
        assert user.email == TEST_USER_DATA['email']
        assert user.first_name == TEST_USER_DATA['first_name']
        assert user.last_name == TEST_USER_DATA['last_name']
        assert user.organization.name == TEST_USER_DATA['organization_name']

        # check this user is org admin
        assert user.is_org_admin

    def test_registration_of_second_org_user(self, request_factory, org_admin):
        request = request_factory.post(reverse('coreuser-list'), TEST_USER_DATA)
        response = CoreUserViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 201

        user = CoreUser.objects.get(username=TEST_USER_DATA['username'])
        assert user.email == TEST_USER_DATA['email']
        assert user.first_name == TEST_USER_DATA['first_name']
        assert user.last_name == TEST_USER_DATA['last_name']
        assert user.organization.name == TEST_USER_DATA['organization_name']
        assert not user.is_active

        # check this user is NOT org admin
        assert not user.is_org_admin

    def test_registration_of_invited_org_user(self, request_factory, org_admin):
        data = TEST_USER_DATA.copy()
        token = create_invitation_token(data['email'], org_admin.organization)
        data['invitation_token'] = token

        request = request_factory.post(reverse('coreuser-list'), data)
        response = CoreUserViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 201

        user = CoreUser.objects.get(username=TEST_USER_DATA['username'])
        assert user.email == TEST_USER_DATA['email']
        assert user.first_name == TEST_USER_DATA['first_name']
        assert user.last_name == TEST_USER_DATA['last_name']
        assert user.organization.name == TEST_USER_DATA['organization_name']
        assert not user.is_active

        # check this user is NOT org admin
        assert not user.is_org_admin

    def test_reused_token_invalidation(self, request_factory, org_admin):
        data = TEST_USER_DATA.copy()
        registered_user = factories.CoreUser.create(is_active=False, email=data['email'], username='user_org')
        token = create_invitation_token(data['email'], org_admin.organization)
        data['invitation_token'] = token

        request = request_factory.post(reverse('coreuser-list'), data)
        response = CoreUserViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 400

    def test_email_mismatch_token_invalidation(self, request_factory, org_admin):
        data = TEST_USER_DATA.copy()
        token = create_invitation_token("foobar@example.com", org_admin.organization)
        data['invitation_token'] = token

        request = request_factory.post(reverse('coreuser-list'), data)
        response = CoreUserViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 400

    def test_registration_with_core_groups(self, request_factory, org_admin):
        data = TEST_USER_DATA.copy()
        groups = factories.CoreGroup.create_batch(2, organization=org_admin.organization)
        data['core_groups'] = [item.pk for item in groups]

        request = request_factory.post(reverse('coreuser-list'), data)
        response = CoreUserViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 201

        user = CoreUser.objects.get(username=TEST_USER_DATA['username'])
        # check that user has groups from the request
        assert set(groups).issubset(set(list(user.core_groups.all())))


@pytest.mark.django_db()
class TestCoreUserUpdate:

    def test_coreuser_update(self, request_factory, org_admin):
        user = factories.CoreUser.create(is_active=False, organization=org_admin.organization, username='org_user')
        pk = user.pk

        data = {
            'is_active': True,
        }
        request = request_factory.patch(reverse('coreuser-detail', args=(pk,)), data)
        request.user = org_admin
        response = CoreUserViewSet.as_view({'patch': 'partial_update'})(request, pk=pk)
        assert response.status_code == 200
        coreuser = CoreUser.objects.get(pk=pk)
        assert coreuser.is_active

    def test_coreuser_update_dif_org(self, request_factory, org_admin):
        dif_org = factories.Organization(name='Another Org')
        user = factories.CoreUser.create(is_active=False, organization=dif_org, username='another_org_user')
        pk = user.pk

        data = {
            'is_active': True,
        }
        request = request_factory.patch(reverse('coreuser-detail', args=(pk,)), data)
        request.user = org_admin
        response = CoreUserViewSet.as_view({'patch': 'partial_update'})(request, pk=pk)
        assert response.status_code == 403

    def test_coreuser_update_groups(self, request_factory, org_admin):
        user = factories.CoreUser.create(is_active=False, organization=org_admin.organization, username='user_org')
        initial_groups = factories.CoreGroup.create_batch(2, organization=user.organization)
        user.core_groups.add(*initial_groups)
        pk = user.pk

        new_groups = factories.CoreGroup.create_batch(2, organization=user.organization)
        data = {
            'core_groups': [item.pk for item in new_groups],
        }
        request = request_factory.patch(reverse('coreuser-detail', args=(pk,)), data)
        request.user = org_admin
        response = CoreUserViewSet.as_view({'patch': 'partial_update'})(request, pk=pk)
        assert response.status_code == 200
        coreuser = CoreUser.objects.get(pk=pk)
        assert set(coreuser.core_groups.all()) == set(new_groups)

    def test_coreuser_profile_update(self, request_factory, org_admin):
        user = factories.CoreUser.create(is_active=False, organization=org_admin.organization, username='org_user')
        pk = user.pk

        data = {'contact_info': "data"}

        request = request_factory.patch(reverse('coreuser-update-profile', args=(pk,)), data)
        request.user = org_admin
        response = CoreUserViewSet.as_view({'patch': 'partial_update'})(request, pk=pk)
        assert response.status_code == 200
        coreuser = CoreUser.objects.get(pk=pk)
        assert coreuser.contact_info == "data"

@pytest.mark.django_db()
class TestCoreUserInvite:

    def test_invitation(self, request_factory, org_admin):
        data = {'emails': [TEST_USER_DATA['email']]}
        request = request_factory.post(reverse('coreuser-invite'), data)
        request.user = org_admin
        response = CoreUserViewSet.as_view({'post': 'invite'})(request)
        assert response.status_code == 200
        assert len(response.data['invitations']) == 1

    def test_invitation_check(self, request_factory, org):
        token = create_invitation_token(TEST_USER_DATA['email'], org)
        request = request_factory.get(reverse('coreuser-invite-check'), {'token': token})
        response = CoreUserViewSet.as_view({'get': 'invite_check'})(request)
        assert response.status_code == 200
        assert response.data['email'] == TEST_USER_DATA['email']
        assert response.data['organization']['organization_uuid'] == org.organization_uuid

    def test_prevent_token_reuse(self, request_factory, org):
        token = create_invitation_token(TEST_USER_DATA['email'], org)
        registered_user = factories.CoreUser.create(is_active=False, email=TEST_USER_DATA['email'], username='user_org')
        request = request_factory.get(reverse('coreuser-invite-check'), {'token': token})
        response = CoreUserViewSet.as_view({'get': 'invite_check'})(request)
        assert response.status_code == 401


@pytest.mark.django_db()
class TestResetPassword(object):

    def test_reset_password_using_default_emailtemplate(self, request_factory, org_member):
        email = org_member.email
        assert list(org_member.organization.emailtemplate_set.all()) == []
        assert list(Organization.objects.filter(name=settings.DEFAULT_ORG)) == []
        request = request_factory.post(reverse('coreuser-reset-password'), {'email': email})
        response = CoreUserViewSet.as_view({'post': 'reset_password'})(request)
        assert response.status_code == 200
        assert response.data['count'] == 1
        assert mail.outbox

        message = mail.outbox[0]
        assert message.to == [email]

        resetpass_url = urljoin(settings.FRONTEND_URL, settings.RESETPASS_CONFIRM_URL_PATH)
        uid = urlsafe_base64_encode(force_bytes(org_member.pk))
        token = default_token_generator.make_token(org_member)
        assert f'{resetpass_url}{uid}/{token}/' in message.body
        assert 'Thanks for using our site!' in message.body

    def test_reset_password_using_org_template(self, request_factory, org_member):
        email = org_member.email

        EmailTemplate.objects.create(
            organization=org_member.organization,
            type=TEMPLATE_RESET_PASSWORD,
            subject='Custom subject',
            template="""
                Custom template
                {{ password_reset_link }}
                """
        )

        request = request_factory.post(reverse('coreuser-reset-password'), {'email': email})
        response = CoreUserViewSet.as_view({'post': 'reset_password'})(request)
        assert response.status_code == 200
        assert response.data['count'] == 1
        assert mail.outbox

        message = mail.outbox[0]
        assert message.to == [email]

        resetpass_url = urljoin(settings.FRONTEND_URL, settings.RESETPASS_CONFIRM_URL_PATH)
        uid = urlsafe_base64_encode(force_bytes(org_member.pk))
        token = default_token_generator.make_token(org_member)
        assert message.subject == 'Custom subject'
        assert 'Custom template' in message.body
        assert f'{resetpass_url}{uid}/{token}/' in message.body

    def test_reset_password_using_default_org_template(self, request_factory, org_member):
        email = org_member.email

        default_organization = factories.Organization(name=settings.DEFAULT_ORG)

        EmailTemplate.objects.create(
            organization=default_organization,
            type=TEMPLATE_RESET_PASSWORD,
            subject='Custom subject',
            template="""
                Custom template
                {{ password_reset_link }}
                """
        )

        request = request_factory.post(reverse('coreuser-reset-password'), {'email': email})
        response = CoreUserViewSet.as_view({'post': 'reset_password'})(request)
        assert response.status_code == 200
        assert response.data['count'] == 1
        assert mail.outbox

        message = mail.outbox[0]
        assert message.to == [email]

        resetpass_url = urljoin(settings.FRONTEND_URL, settings.RESETPASS_CONFIRM_URL_PATH)
        uid = urlsafe_base64_encode(force_bytes(org_member.pk))
        token = default_token_generator.make_token(org_member)
        assert message.subject == 'Custom subject'
        assert 'Custom template' in message.body
        assert f'{resetpass_url}{uid}/{token}/' in message.body

    def test_reset_password_no_user(self, request_factory):
        request = request_factory.post(reverse('coreuser-reset-password'), {'email': 'foo@example.com'})
        response = CoreUserViewSet.as_view({'post': 'reset_password'})(request)
        assert response.status_code == 200
        assert response.data['count'] == 0

    def test_reset_password_check(self, request_factory, reset_password_request):
        user, uid, token = reset_password_request
        data = {
            'uid': uid,
            'token': token,
        }
        request = request_factory.post(reverse('coreuser-reset-password-check'), data)
        response = CoreUserViewSet.as_view({'post': 'reset_password_check'})(request)
        assert response.status_code == 200
        assert response.data['success'] is True

    def test_reset_password_check_expired(self, request_factory, reset_password_request):
        user, uid, token = reset_password_request
        data = {
            'uid': uid,
            'token': token,
        }
        mock_date = date.today() + timedelta(int(settings.PASSWORD_RESET_TIMEOUT_DAYS) + 1)
        with mock.patch('django.contrib.auth.tokens.PasswordResetTokenGenerator._today', return_value=mock_date):
            request = request_factory.post(reverse('coreuser-reset-password-check'), data)
            response = CoreUserViewSet.as_view({'post': 'reset_password_check'})(request)
            assert response.status_code == 200
            assert response.data['success'] is False

    def test_reset_password_confirm(self, request_factory, reset_password_request):
        test_password = '5UU74e7nfU'
        user, uid, token = reset_password_request
        data = {
            'new_password1': test_password,
            'new_password2': test_password,
            'uid': uid,
            'token': token,
        }
        request = request_factory.post(reverse('coreuser-reset-password-confirm'), data)
        response = CoreUserViewSet.as_view({'post': 'reset_password_confirm'})(request)
        assert response.status_code == 200

        # check that password was changed
        updated_user = CoreUser.objects.get(pk=user.pk)
        assert updated_user.check_password(test_password)

    def test_reset_password_confirm_diff_passwords(self, request_factory, reset_password_request):
        test_password1 = '5UU74e7nfU'
        test_password2 = '5UU74e7nfUa'
        user, uid, token = reset_password_request
        data = {
            'new_password1': test_password1,
            'new_password2': test_password2,
            'uid': uid,
            'token': token,
        }
        request = request_factory.post(reverse('coreuser-reset-password-confirm'), data)
        response = CoreUserViewSet.as_view({'post': 'reset_password_confirm'})(request)
        assert response.status_code == 400  # validation error (password fields didn't match)

    def test_reset_password_confirm_token_expired(self, request_factory, reset_password_request):
        test_password = '5UU74e7nfU'
        user, uid, token = reset_password_request
        data = {
            'new_password1': test_password,
            'new_password2': test_password,
            'uid': uid,
            'token': token,
        }
        mock_date = date.today() + timedelta(int(settings.PASSWORD_RESET_TIMEOUT_DAYS) + 1)
        with mock.patch('django.contrib.auth.tokens.PasswordResetTokenGenerator._today', return_value=mock_date):
            request = request_factory.post(reverse('coreuser-reset-password-confirm'), data)
            response = CoreUserViewSet.as_view({'post': 'reset_password_confirm'})(request)
            assert response.status_code == 400  # validation error (the token is expired)


@pytest.mark.django_db()
class TestCoreUserRead(object):

    keys = {'id', 'core_user_uuid', 'first_name', 'last_name', 'email', 'username', 'is_active', 'title',
            'contact_info', 'privacy_disclaimer_accepted', 'organization', 'core_groups', 'user_type', 'survey_status'}

    def test_coreuser_list(self, request_factory, org_member):
        factories.CoreUser.create(organization=org_member.organization, username='another_user')  # 2nd user of the org
        factories.CoreUser.create(organization=factories.Organization(name='another otg'),
                                  username='yet_another_user')  # user of the different org
        request = request_factory.get(reverse('coreuser-list'))
        request.user = org_member
        response = CoreUserViewSet.as_view({'get': 'list'})(request)
        assert response.status_code == 200
        data = response.data
        assert len(data) == 2
        assert set(data[0].keys()) == self.keys

    def test_coreuser_retrieve(self, request_factory, org_member):
        core_user = factories.CoreUser.create(organization=org_member.organization, username='another_user')

        request = request_factory.get(reverse('coreuser-detail', args=(core_user.pk,)))
        request.user = org_member
        response = CoreUserViewSet.as_view({'get': 'retrieve'})(request, pk=core_user.pk)
        assert response.status_code == 200
        assert set(response.data.keys()) == self.keys

    def test_coreuser_retrieve_me(self, request_factory, org_member):
        request = request_factory.get(reverse('coreuser-list'))
        request.user = org_member
        response = CoreUserViewSet.as_view({'get': 'me'})(request)
        assert response.status_code == 200
        assert response.data['username'] == org_member.username


@pytest.mark.django_db()
class TestNotification:

    def test_notification(self, request_factory):
        dif_org = factories.Organization(name='Another Org')
        data = {
            "organization_uuid": dif_org.organization_uuid,
            "notification_messages": "message"
        }
        request = request_factory.post(reverse('coreuser-notification'), data)
        response = CoreUserViewSet.as_view({'post': 'notification'})(request)
        assert response.status_code == 200
