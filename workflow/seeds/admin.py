"""
Populate Appointments and Contacts with fake data.
"""
import string

import requests
from django.conf import settings
from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import reverse, re_path
from django.http import HttpResponseRedirect, HttpRequest
from django.template.response import TemplateResponse
from django.utils.html import format_html
from oauth2_provider_jwt.utils import generate_payload, encode_jwt
from rest_framework.request import Request

from gateway.models import LogicModule
from gateway.request import GatewayRequest
from workflow.models import Organization
from .data import appointments, contacts, SEED_DATA


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "create_date", "edit_date", "organization_actions")
    readonly_fields = ("organization_actions",)

    def get_urls(self):
        urls = super().get_urls()
        custom_url = [
            re_path(
                r"^(?P<organization_uuid>.+)/seed/$",
                self.admin_site.admin_view(self.provide_seed),
                name="organization-seed",
            )
        ]
        return custom_url + urls

    def organization_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Seed</a>&nbsp;',
            reverse("admin:organization-seed", args=[obj.pk]),
        )

    organization_actions.short_description = "Organization Actions"
    organization_actions.allow_tags = True

    @staticmethod
    def _create_headers(user, organization_uuid: string) -> dict:
        extra_data = {
            'organization_uuid': organization_uuid,
            'core_user_uuid': user.core_user_uuid,
            'username': user.username,
        }
        payload = generate_payload(settings.JWT_ISSUER, expires_in=600, **extra_data)
        token = encode_jwt(payload)
        return {
            'Authorization': 'JWT ' + token,
            'Content-Type': 'application/json'
        }

    @staticmethod
    def _validate_empty_data(request: HttpRequest, headers: dict) -> bool:
        """Check if logic modules databases are empty."""
        is_empty = True
        for logic_module_name in SEED_DATA.keys():
            logic_module = LogicModule.objects.get(name=logic_module_name)
            for model_endpoint in SEED_DATA[logic_module_name].keys():
                url = f'{logic_module.endpoint}/{model_endpoint}/'
                response = requests.get(url, headers=headers)
                if not response.status_code == 200:
                    messages.error(request, f"Seed Data Configuration Error: 404 endpoint not found: {url}")
                    return redirect(request.META['HTTP_REFERER'])
                if not response.json()['count'] == 0:
                    messages.error(request, f"No data seeded because there is already data in {url}.")
                    is_empty = False
        return is_empty

    def provide_seed(self, request, organization_uuid: string):
        headers = self._create_headers(request.user, organization_uuid)

        if not self._validate_empty_data(request, headers):
            return redirect(request.META['HTTP_REFERER'])

        # Now seed (POST) data


        organization = Organization.objects.get(organization_uuid=organization_uuid)
        messages.success(request, f"{organization} Something should be seeded.")
        return redirect(request.META['HTTP_REFERER'])
