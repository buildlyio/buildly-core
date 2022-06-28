import pytest

from django.core.handlers.wsgi import WSGIRequest

from factories.workflow_models import Organization

from gateway.exceptions import ServiceDoesNotExist
from gateway.permissions import AllowLogicModuleGroup
from gateway.views import APIGatewayView
from core.tests.fixtures import (
    auth_api_client,
    auth_superuser_api_client,
    core_group,
    logic_module,
    org,
    org_admin,
    superuser,
)


@pytest.mark.django_db()
class TestAllowLogicModuleGroup:
    def test_has_permission_superuser_success(
        self, auth_superuser_api_client, superuser
    ):
        """
        Superusers are able to access all services
        """
        request = WSGIRequest(
            auth_superuser_api_client._base_environ(
                **auth_superuser_api_client._credentials
            )
        )
        request.user = superuser
        kwargs = {'kwargs': {'service': 'test'}, 'request': request}
        permission_obj = AllowLogicModuleGroup()
        view = APIGatewayView(**kwargs)

        result = permission_obj.has_permission(kwargs['request'], view)
        assert result

    def test_has_permission_normal_user_service_doesnt_exist(
        self, auth_api_client, org_admin, org
    ):
        request = WSGIRequest(
            auth_api_client._base_environ(**auth_api_client._credentials)
        )
        request.user = org_admin
        kwargs = {'kwargs': {'service': 'test'}, 'request': request}
        permission_obj = AllowLogicModuleGroup()
        view = APIGatewayView(**kwargs)

        with pytest.raises(ServiceDoesNotExist):
            permission_obj.has_permission(kwargs['request'], view)

    def test_has_permission_normal_user_no_restrictions(
        self, auth_api_client, org_admin, org, logic_module
    ):
        """
        Services without permission groups can be accessed by everybody
        """
        request = WSGIRequest(
            auth_api_client._base_environ(**auth_api_client._credentials)
        )
        request.user = org_admin
        kwargs = {'kwargs': {'service': logic_module.name}, 'request': request}
        permission_obj = AllowLogicModuleGroup()
        view = APIGatewayView(**kwargs)

        result = permission_obj.has_permission(kwargs['request'], view)
        assert result

    def test_has_permission_global_level_permission(
        self, auth_api_client, org_admin, org, logic_module, core_group
    ):
        """
        Global level permissions of a service are applied to all users who try to access it
        """
        core_group.is_global = True
        core_group.is_org_level = False
        core_group.organization = None
        core_group.save()
        logic_module.core_groups.add(core_group)

        request = WSGIRequest(
            auth_api_client._base_environ(**auth_api_client._credentials)
        )
        request.user = org_admin
        kwargs = {'kwargs': {'service': logic_module.name}, 'request': request}
        permission_obj = AllowLogicModuleGroup()
        view = APIGatewayView(**kwargs)

        result = permission_obj.has_permission(kwargs['request'], view)
        assert result

    def test_has_permission_normal_user_org_level_permission(
        self, auth_api_client, org_admin, org, logic_module
    ):
        """
        Organization level permissions of a service are applied to users of a specific org
        """
        org_admin_group = org_admin.core_groups.all().first()
        logic_module.core_groups.add(org_admin_group)

        request = WSGIRequest(
            auth_api_client._base_environ(**auth_api_client._credentials)
        )
        request.user = org_admin
        kwargs = {'kwargs': {'service': logic_module.name}, 'request': request}
        permission_obj = AllowLogicModuleGroup()
        view = APIGatewayView(**kwargs)

        result = permission_obj.has_permission(kwargs['request'], view)
        assert result

    def test_has_permission_normal_user_org_level_diff_org(
        self, auth_api_client, org_admin, org, logic_module, core_group
    ):
        """
        Organization level permissions of a service aren't applied to users from an org different to the one
        from the permissions
        """
        core_group.is_global = False
        core_group.is_org_level = True
        core_group.organization = Organization.create()
        core_group.save()
        logic_module.core_groups.add(core_group)

        request = WSGIRequest(
            auth_api_client._base_environ(**auth_api_client._credentials)
        )
        request.user = org_admin
        kwargs = {'kwargs': {'service': logic_module.name}, 'request': request}
        permission_obj = AllowLogicModuleGroup()
        view = APIGatewayView(**kwargs)

        result = permission_obj.has_permission(kwargs['request'], view)
        assert result
