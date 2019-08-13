"""
Populate Appointments and Contacts with fake data.
"""
import string

from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import reverse, re_path
from django.utils.html import format_html

from workflow.models import Organization

from workflow.seeds.seed import SeedEnv, SeedDataMesh, SeedBifrost, SeedLogicModule

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

    @staticmethod
    def provide_seed(request, organization_uuid: string):
        # Get and validate organization
        try:
            organization = Organization.objects.get(organization_uuid=organization_uuid)
        except Organization.DoesNotExist:
            messages.error(request, "Organization not found. Was it saved? It must be before seeding is possible.")
            return redirect(request.META["HTTP_REFERER"])

        # Create SeedEnv
        seed_env = SeedEnv(request, organization_uuid)

        # Validate empty organization
        if not seed_env.is_empty(data.SEED_DATA):
            return redirect(request.META["HTTP_REFERER"])

        # Create SeedDataMesh and validate data mesh relationship exists
        seed_data_mesh = SeedDataMesh(data.join_records)
        if not seed_data_mesh.validate_relationship_exists(request):
            return redirect(request.META["HTTP_REFERER"])

        # Seed bifrost data
        seed_bifrost = SeedBifrost(organization,
                                   data.workflowleveltypes,
                                   data.workflowlevel2s)
        level1_uuid, wfl2_uuid_map, org_core_user_uuids = seed_bifrost.seed()

        # Seed profiletypes and build profiletype_map
        profiletype_map = seed_env.get_profile_types_map(data.profiletypes)

        # Seed product categories and build product_category_map
        product_category_map = seed_env.get_product_category_map(data.product_categories)

        # Seed SEED_DATA
        seed_env.pk_maps = {
            "workflowlevel1": {"49a4c9d7-8b72-434b-8a48-24540f65a2f3": level1_uuid},
            "workflowlevel2": wfl2_uuid_map,
            "profiletypes": profiletype_map,
            "categories": product_category_map,
            "org_core_user_uuids": org_core_user_uuids,
        }
        seed = SeedLogicModule(seed_env, data.SEED_DATA)
        seed.seed()

        # Seed Data Mesh JoinRecords
        seed_data_mesh.seed(seed_env.pk_maps, organization)

        messages.success(request, f"{organization} - Seed successful.")
        return redirect(request.META["HTTP_REFERER"])
