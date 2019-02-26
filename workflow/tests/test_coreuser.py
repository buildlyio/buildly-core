from datetime import date, timedelta
from urllib.parse import urljoin
from unittest import mock

import pytest
from django.core import mail
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.reverse import reverse

import factories
from workflow.views import CoreUserViewSet
from workflow import models as wfm
from workflow.jwt_utils import create_invitation_token
from .fixtures import org, org_admin, org_member, group_org_admin, reset_password_request, TEST_USER_DATA


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
    request.user = org_member.user
    response = CoreUserViewSet.as_view({'get': 'list'})(request)
    assert response.status_code == 200

    # has no permission
    request = request_factory.post(reverse('coreuser-invite'))
    request.user = org_member.user
    response = CoreUserViewSet.as_view({'post': 'invite'})(request)
    assert response.status_code == 403

    # has permission
    request = request_factory.get(reverse('coreuser-detail', args=(pk,)))
    request.user = org_member.user
    response = CoreUserViewSet.as_view({'get': 'retrieve'})(request, pk=pk)
    assert response.status_code == 200

    # has no permission
    request = request_factory.put(reverse('coreuser-detail', args=(pk,)))
    request.user = org_member.user
    response = CoreUserViewSet.as_view({'put': 'update'})(request, pk=pk)
    assert response.status_code == 403

    # has no permission
    request = request_factory.patch(reverse('coreuser-detail', args=(1,)))
    request.user = org_member.user
    response = CoreUserViewSet.as_view({'patch': 'partial_update'})(request,
                                                                    pk=1)
    assert response.status_code == 403


@pytest.mark.django_db()
def test_registration_fail(request_factory):
    # check that all fields in USER_DATA are required
    for field_name in TEST_USER_DATA.keys():
        data = TEST_USER_DATA.copy()
        data.pop(field_name)
        request = request_factory.post(reverse('coreuser-list'), data)
        response = CoreUserViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 400


@pytest.mark.django_db()
def test_registration_of_first_org_user(request_factory, group_org_admin):
    request = request_factory.post(reverse('coreuser-list'), TEST_USER_DATA)
    response = CoreUserViewSet.as_view({'post': 'create'})(request)
    assert response.status_code == 201

    coreuser = wfm.CoreUser.objects.get(user__username=
                                        TEST_USER_DATA['username'])
    user = coreuser.user
    assert user.email == TEST_USER_DATA['email']
    assert user.first_name == TEST_USER_DATA['first_name']
    assert user.last_name == TEST_USER_DATA['last_name']
    assert coreuser.organization.name == TEST_USER_DATA['organization_name']
    assert user.is_active

    # check this user is org admin
    assert group_org_admin in user.groups.all()


@pytest.mark.django_db()
def test_registration_of_second_org_user(request_factory, org_admin):
    request = request_factory.post(reverse('coreuser-list'), TEST_USER_DATA)
    response = CoreUserViewSet.as_view({'post': 'create'})(request)
    assert response.status_code == 201

    coreuser = wfm.CoreUser.objects.get(user__username=
                                        TEST_USER_DATA['username'])
    user = coreuser.user
    assert user.email == TEST_USER_DATA['email']
    assert user.first_name == TEST_USER_DATA['first_name']
    assert user.last_name == TEST_USER_DATA['last_name']
    assert coreuser.organization.name == TEST_USER_DATA['organization_name']
    assert not user.is_active

    # check this user is NOT org admin
    group_org_admin = org_admin.user.groups.get(name=
                                                wfm.ROLE_ORGANIZATION_ADMIN)
    assert group_org_admin not in user.groups.all()


@pytest.mark.django_db()
def test_registration_of_invited_org_user(request_factory, org_admin):
    data = TEST_USER_DATA.copy()
    token = create_invitation_token(data['email'], org_admin.organization)
    data['invitation_token'] = token

    request = request_factory.post(reverse('coreuser-list'), data)
    response = CoreUserViewSet.as_view({'post': 'create'})(request)
    assert response.status_code == 201

    coreuser = wfm.CoreUser.objects.get(user__username=TEST_USER_DATA['username'])
    user = coreuser.user
    assert user.email == TEST_USER_DATA['email']
    assert user.first_name == TEST_USER_DATA['first_name']
    assert user.last_name == TEST_USER_DATA['last_name']
    assert coreuser.organization.name == TEST_USER_DATA['organization_name']
    assert user.is_active

    # check this user is NOT org admin
    group_org_admin = org_admin.user.groups.get(name=
                                                wfm.ROLE_ORGANIZATION_ADMIN)
    assert group_org_admin not in user.groups.all()


@pytest.mark.django_db()
def test_coreuser_update(request_factory, org_admin):
    coreuser = factories.CoreUser.create(user__is_active=False)
    pk = coreuser.pk

    data = {
        'is_active': True,
    }
    request = request_factory.patch(reverse('coreuser-detail', args=(pk,)), data)
    request.user = org_admin.user
    response = CoreUserViewSet.as_view({'patch': 'partial_update'})(request,
                                                                    pk=pk)
    assert response.status_code == 200
    coreuser = wfm.CoreUser.objects.get(pk=pk)
    assert coreuser.user.is_active
    assert coreuser.is_active


@pytest.mark.django_db()
def test_invitation(request_factory, org_admin):
    data = {'emails': [TEST_USER_DATA['email']]}
    request = request_factory.post(reverse('coreuser-invite'), data)
    request.user = org_admin.user
    response = CoreUserViewSet.as_view({'post': 'invite'})(request)
    assert response.status_code == 200
    assert len(response.data['invitations']) == 1


@pytest.mark.django_db()
def test_invitation_check(request_factory, org):
    token = create_invitation_token(TEST_USER_DATA['email'], org)
    request = request_factory.get(reverse('coreuser-invite-check'),
                              {'token': token})
    response = CoreUserViewSet.as_view({'get': 'invite_check'})(request)
    assert response.status_code == 200
    assert response.data['email'] == TEST_USER_DATA['email']
    assert response.data['organization']['organization_uuid'] == \
        str(org.organization_uuid)


@pytest.mark.django_db()
class TestResetPassword(object):

    def test_reset_password(self, request_factory, org_member):
        user = org_member.user
        email = user.email
        request = request_factory.post(reverse('coreuser-reset-password'), {'email': email})
        response = CoreUserViewSet.as_view({'post': 'reset_password'})(request)
        assert response.status_code == 200
        assert response.data['count'] == 1
        assert mail.outbox

        message = mail.outbox[0]
        assert message.to == [email]

        resetpass_url = urljoin(settings.FRONTEND_URL, settings.RESETPASS_CONFIRM_URL_PATH)
        uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
        token = default_token_generator.make_token(user)
        assert f'{resetpass_url}{uid}/{token}/' in message.body

    def test_reset_password_using_org_template(self, request_factory, org_member):
        user = org_member.user
        email = user.email

        wfm.EmailTemplate.objects.create(
            organization=org_member.organization,
            type=wfm.TEMPLATE_RESET_PASSWORD,
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
        uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
        token = default_token_generator.make_token(user)
        assert message.subject == 'Custom subject'
        assert 'Custom template' in message.body
        assert f'{resetpass_url}{uid}/{token}/' in message.body

    def test_reset_password_no_user(self, request_factory):
        request = request_factory.post(reverse('coreuser-reset-password'), {'email': 'foo@example.com'})
        response = CoreUserViewSet.as_view({'post': 'reset_password'})(request)
        assert response.status_code == 200
        assert response.data['count'] == 0

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
        updated_user = User.objects.get(pk=user.pk)
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
