import json
import string
from copy import deepcopy
from datetime import date, timedelta
from typing import Tuple

import requests
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpRequest
from oauth2_provider_jwt.utils import generate_payload, encode_jwt

from gateway.models import LogicModule
from workflow.models import (
    Organization,
    WorkflowLevel1,
    WorkflowLevel2,
    WorkflowLevelType,
    CoreUser,
)
from . import data


def _create_headers(user, organization_uuid: string) -> dict:
    extra_data = {
        "organization_uuid": organization_uuid,
        "core_user_uuid": user.core_user_uuid,
        "username": user.username,
    }
    payload = generate_payload(settings.JWT_ISSUER, expires_in=600, **extra_data)
    token = encode_jwt(payload)
    return {"Authorization": "JWT " + token, "Content-Type": "application/json"}


def _validate_empty_data(request: HttpRequest, headers: dict) -> bool:
    """Check if logic modules databases are empty."""
    is_empty = True
    for logic_module_name in data.SEED_DATA.keys():
        logic_module = LogicModule.objects.get(name=logic_module_name)
        for model_endpoint in data.SEED_DATA[logic_module_name].keys():
            model_endpoint_dict = data.SEED_DATA[logic_module_name][model_endpoint]
            if "validate" in model_endpoint_dict.keys() and not model_endpoint_dict["validate"]:
                continue
            url = f"{logic_module.endpoint}/{model_endpoint}/"
            response = requests.get(url, headers=headers)
            if not response.status_code == 200:
                messages.error(
                    request,
                    f"Seed Data Configuration Error: 404 endpoint not found: GET {url}",
                )
                return redirect(request.META["HTTP_REFERER"])
            if "results" in response.json():
                if response.json()["results"]:
                    is_empty = False
                    messages.error(
                        request,
                        f"No data seeded because there is already data in {url}.",
                    )
    return is_empty


def _update_value_data(
    update_map: dict, value_data: list, value_field_name: str
) -> list:
    """Update every item in value_data['value_field_name'] with the help of the update_map."""
    for old_value, new_value in update_map.items():
        for value_item in value_data:
            if value_item[value_field_name] == old_value:
                value_item[value_field_name] = new_value
    return value_data


def _update_date(value_data: list, date_field_name: str, days_delta: int) -> list:
    """Update the specified dates in the list."""
    for item in value_data:
        if date_field_name in item.keys():
            item[date_field_name] = date.today() + timedelta(days=days_delta)
    return value_data


def _seed_bifrost_data(organization: Organization) -> Tuple[dict, str, dict]:
    """Seed WorkflowLevelTypes, WorkflowLevel1, WorkflowLevel2s."""
    # Seed WorkflowLevelTypes
    wfl_types_map = {}
    wfl_types = deepcopy(
        data.workflowleveltypes
    )  # for preventing changes on (initial) seed.dict
    for wfl_type_item in wfl_types:
        old_wfltypes_uuid = wfl_type_item.pop("uuid")
        wfl_type, _ = WorkflowLevelType.objects.get_or_create(**wfl_type_item)
        wfl_types_map[old_wfltypes_uuid] = wfl_type.uuid

    # Seed WorkflowLevel1
    wfl1, _ = WorkflowLevel1.objects.get_or_create(
        organization=organization, defaults={"name": "Seed Data prep"}
    )

    # Seed WorkflowLevel2s
    wfl2_copy = deepcopy(data.workflowlevel2s)
    workflowlevel2s = _update_value_data(wfl_types_map, wfl2_copy, "type")
    workflowlevel2s = _update_value_data({18: wfl1}, workflowlevel2s, "workflowlevel1")
    workflowlevel2s = _update_date(workflowlevel2s, "end_date", 20)
    wfl2_uuid_map = {}
    for wfl2_dict in workflowlevel2s:
        wfl2_dict["type_id"] = wfl2_dict.pop("type")
        old_level2_uuid = wfl2_dict.pop("level2_uuid")
        wfl2 = WorkflowLevel2.objects.create(**wfl2_dict)
        wfl2_uuid_map[old_level2_uuid] = str(wfl2.level2_uuid)

    # Seed CoreUsers
    def _get_unique_seeddata_username():
        core_users = CoreUser.objects.filter(username__startswith="SeedData")
        return f"SeedData{core_users.count() + 1}"

    core_user_map = {}
    for core_user_dict in deepcopy(data.core_users):
        old_core_user_uuid = core_user_dict.pop("core_user_uuid")
        core_user_dict["username"] = _get_unique_seeddata_username()
        core_user = CoreUser.objects.create(
            **{**core_user_dict, **{"organization": organization}}
        )
        core_user_map[old_core_user_uuid] = str(core_user.core_user_uuid)

    return wfl2_uuid_map, str(wfl1.level1_uuid), core_user_map


def _get_profile_types_map(headers, profiletypes):
    """
    Build map of location.profiletypes.
    In case the profiletypes are not there, they get created.
    """
    profile_type_map = {}
    logic_module = LogicModule.objects.get(name="location")
    url = f"{logic_module.endpoint}/profiletypes/"
    response = requests.get(url, headers=headers)
    results = json.loads(response.content)["results"]
    # get existing profiletypes
    for seed_pt in profiletypes:
        for pt in results:
            if pt["name"] == seed_pt["name"]:
                profile_type_map[seed_pt["id"]] = pt["id"]
                break
    # create non-existing profiletypes
    for seed_pt in profiletypes:
        if seed_pt["id"] not in profile_type_map.keys():
            response = requests.post(url, data=json.dumps(seed_pt), headers=headers)
            profile_type_id = json.loads(response.content)["id"]
            profile_type_map[seed_pt["id"]] = profile_type_id
    return profile_type_map


def _build_product_category_map(headers, categories):
    product_category_map = {}
    logic_module = LogicModule.objects.get(name="products")
    url = f"{logic_module.endpoint}/categories/?is_global=true"
    response = requests.get(url, headers=headers)
    categories = deepcopy(categories)
    for cat in categories:
        for response_cat in response.json():
            if response_cat["name"] == cat["name"]:
                product_category_map[cat["id"]] = response_cat["id"]
                break
    # create non-existing categories
    for cat in categories:
        if cat["id"] not in product_category_map.keys():
            if cat["parent"]:
                cat["parent"] = product_category_map[cat["parent"]]
            response = requests.post(url, data=json.dumps(cat), headers=headers)
            category_id = response.json()["id"]
            product_category_map[cat["id"]] = category_id
    return product_category_map
