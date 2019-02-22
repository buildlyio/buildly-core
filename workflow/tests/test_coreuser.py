import pytest
from rest_framework.reverse import reverse

import factories
from workflow.views import CoreUserViewSet
from workflow import models as wfm
from workflow.jwt_utils import create_invitation_token
from .fixtures import org, org_admin, org_member, group_org_admin, TEST_USER_DATA


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
def test_reset_password(request_factory):
    request = request_factory.post(reverse('coreuser-reset-password'), {'email': 'test@example.com'})
    response = CoreUserViewSet.as_view({'post': 'reset_password'})(request)
    assert response.status_code == 200
