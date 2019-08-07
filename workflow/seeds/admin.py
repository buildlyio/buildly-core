"""
Populate Appointments and Contacts with fake data.
"""
import string

from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import reverse, re_path
from django.utils.html import format_html

from gateway.models import LogicModule
from workflow.models import Organization

from workflow.seeds.seed import SeedEnv, Seed
from workflow.seeds.utils import (_create_headers,
                                  _validate_empty_data,
                                  _seed_bifrost_data,
                                  _get_profile_types_map,
                                  _build_product_category_map)
from . import data


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

    def provide_seed(self, request, organization_uuid: string):
        headers = _create_headers(request.user, organization_uuid)

        if not _validate_empty_data(request, headers):
            return redirect(request.META["HTTP_REFERER"])

        organization = Organization.objects.get(organization_uuid=organization_uuid)

        # Seed bifrost data
        wfl2_uuid_map, level1_uuid, core_user_uuid_map = _seed_bifrost_data(organization)

        # Seed profiletypes
        profiletype_map = _get_profile_types_map(headers, data.profiletypes)

        # Build product_category_map
        product_category_map = _build_product_category_map(headers, data.product_categories)

        # Seed SEED_DATA
        pk_maps = {
            "workflowlevel1": {"49a4c9d7-8b72-434b-8a48-24540f65a2f3": level1_uuid},
            "workflowlevel2": wfl2_uuid_map,
            "profiletypes": profiletype_map,
            "coreusers": core_user_uuid_map,
            "categories": product_category_map,
        }
        seed_env = SeedEnv(headers)
        for logic_module_name in data.SEED_DATA.keys():
            logic_module = LogicModule.objects.get(name=logic_module_name)
            for model_endpoint in data.SEED_DATA[logic_module_name].keys():
                url = f"{logic_module.endpoint}/{model_endpoint}/"
                seed = Seed(
                    seed_env,
                    url,
                    pk_maps,
                    **data.SEED_DATA[logic_module_name][model_endpoint],
                )
                pk_map = seed.perform()
                pk_maps[model_endpoint] = pk_map

        messages.success(request, f"{organization} - Seed successful.")
        return redirect(request.META["HTTP_REFERER"])
