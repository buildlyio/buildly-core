import json
import logging
import string
from copy import deepcopy
from datetime import timedelta
from typing import List, Tuple

import requests
from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest
from django.utils.timezone import now

from oauth2_provider_jwt.utils import generate_payload, encode_jwt

from datamesh.models import LogicModuleModel, Relationship, JoinRecord
from gateway.models import LogicModule
from workflow.models import CoreUser, Organization, WorkflowLevelType, WorkflowLevel1, WorkflowLevel2

logger = logging.getLogger(__name__)


class SeedEnv:

    def __init__(self,
                 request: HttpRequest,
                 organization_uuid: string,
                 pk_maps: dict = {}):
        self.headers = self._create_headers(request.user, organization_uuid)
        self.request = request
        self.pk_maps = pk_maps

    @staticmethod
    def _create_headers(user: CoreUser, organization_uuid: string) -> dict:
        extra_data = {
            "organization_uuid": organization_uuid,
            "core_user_uuid": user.core_user_uuid,
            "username": user.username,
        }
        payload = generate_payload(settings.JWT_ISSUER, expires_in=600, **extra_data)
        token = encode_jwt(payload)
        return {"Authorization": "JWT " + token, "Content-Type": "application/json"}

    def is_empty(self, seed_data: dict) -> bool:
        """Check if logic modules databases are empty."""
        is_empty = True
        for logic_module_name in seed_data.keys():
            try:
                logic_module = LogicModule.objects.get(name=logic_module_name)
            except LogicModule.DoesNotExist:
                messages.error(
                    self.request,
                    f"Seed Data Configuration Error: LogicModule does not exist: {logic_module_name}",
                )
            for model_endpoint in seed_data[logic_module_name].keys():
                model_endpoint_dict = seed_data[logic_module_name][model_endpoint]
                if "validate" in model_endpoint_dict.keys() and not model_endpoint_dict["validate"]:
                    continue
                url = f"{logic_module.endpoint}/{model_endpoint}/"
                response = requests.get(url, headers=self.headers)
                if not response.status_code == 200:
                    is_empty = False
                    messages.error(
                        self.request,
                        f"Seed Data Configuration Error: 404 endpoint not found: GET {url}",
                    )
                if "results" in response.json():
                    if response.json()["results"]:
                        is_empty = False
                        messages.error(
                            self.request,
                            f"No data seeded because there is already data in {url}.",
                        )
        return is_empty

    def get_profile_types_map(self, profiletypes: Tuple[dict]):
        """
        Build map of location.profiletypes.
        In case the profiletypes are not there, they get created.
        """
        profile_type_map = {}
        logic_module = LogicModule.objects.get(name="location")
        url = f"{logic_module.endpoint}/profiletypes/"
        response = requests.get(url, headers=self.headers)
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
                response = requests.post(url, data=json.dumps(seed_pt), headers=self.headers)
                profile_type_id = json.loads(response.content)["id"]
                profile_type_map[seed_pt["id"]] = profile_type_id
        return profile_type_map

    def get_product_category_map(self, categories: Tuple[dict]):
        """
        Build map for product.Categories.
        In case the categories are not there, they get created.
        """
        product_category_map = {}
        logic_module = LogicModule.objects.get(name="products")
        url = f"{logic_module.endpoint}/categories/?is_global=true"
        response = requests.get(url, headers=self.headers)
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
                response = requests.post(url, data=json.dumps(cat), headers=self.headers)
                category_id = response.json()["id"]
                product_category_map[cat["id"]] = category_id
        return product_category_map


class SeedBase:

    @staticmethod
    def update_field(update_map: dict, data: list, field_name: str) -> list:
        """Update every item in data['field_name'] with the help of the update_map."""
        for old_value, new_value in update_map.items():
            for item in data:
                if isinstance(item[field_name], list):
                    for i, list_item in enumerate(item[field_name]):
                        if list_item == old_value:
                            item[field_name][i] = new_value
                else:
                    if item[field_name] == old_value:
                        item[field_name] = new_value
        return data

    @staticmethod
    def update_dates(value_data: list, date_field_name: str, days_delta: int) -> list:
        """Update the specified dates in the list."""
        for item in value_data:
            if date_field_name in item.keys():
                if isinstance(days_delta, dict):
                    new_date = now() + timedelta(**days_delta)
                else:
                    new_date = now() + timedelta(days=days_delta)
                item[date_field_name] = new_date.isoformat()
        return value_data


class SeedLogicModule(SeedBase):

    def __init__(
        self,
        seed_env,
        seed_data: dict,
        **kwargs
    ):
        self.seed_env = seed_env
        self.seed_data = deepcopy(seed_data)

    def _update_pk_fields(self, update_fields_dict: dict, post_data: list):
        """Update every item in post_data['field_name'] with the help of the map."""
        for field_name, endpoint in update_fields_dict.items():
            update_map = self.seed_env.pk_maps[endpoint]
            self.update_field(update_map, post_data, field_name)

    def _update_date_fields(self, update_dates_dict: dict, post_data: list):
        """Update the specified dates in the list."""
        for date_field_name, days_delta in update_dates_dict.items():
            self.update_dates(post_data, date_field_name, days_delta)

    def post_create_requests(self, url, data):
        responses = []
        for entry in data:
            responses.append(
                requests.post(
                    url, data=json.dumps(entry), headers=self.seed_env.headers
                )
            )
            if responses[-1].status_code != 201:
                logger.error(responses[-1].content)
                logger.error(json.dumps(entry))
        return responses

    def _build_map(self, responses, data):
        pk_map = {}
        for i, entry in enumerate(data):
            try:
                pk_map[entry["id"]] = responses[i].json()["id"]
            except KeyError:
                raise KeyError(f"Key 'id' not found in {entry}")
        return pk_map

    def seed(self):
        for logic_module_name in self.seed_data.keys():
            logic_module = LogicModule.objects.get(name=logic_module_name)
            for model_endpoint in self.seed_data[logic_module_name].keys():
                post_data = self.seed_data[logic_module_name][model_endpoint]["data"]
                self._update_pk_fields(
                    self.seed_data[logic_module_name][model_endpoint].get("update_fields", {}),
                    post_data
                )
                self._update_date_fields(
                    self.seed_data[logic_module_name][model_endpoint].get("update_dates", {}),
                    post_data
                )
                responses = self.post_create_requests(
                    f"{logic_module.endpoint}/{model_endpoint}/",
                    post_data
                )
                self.seed_env.pk_maps[model_endpoint] = self._build_map(responses, post_data)


class SeedDataMesh(SeedBase):

    def __init__(self, join_records_data):
        self.join_records_data = deepcopy(join_records_data)

    @staticmethod
    def _get_relationship(origin_lmm: LogicModuleModel, related_lmm: LogicModuleModel) -> Relationship:
        return Relationship.objects.get(
            key=f"{origin_lmm.model.lower()}_{related_lmm.model.lower()}_relationship",
            origin_model=origin_lmm,
            related_model=related_lmm
        )

    def validate_relationship_exists(self, request) -> bool:
        for entry in deepcopy(self.join_records_data):
            origin_lmm = LogicModuleModel.objects.get_by_concatenated_model_name(entry["origin_model_name"])
            related_lmm = LogicModuleModel.objects.get_by_concatenated_model_name(entry["related_model_name"])
            try:
                self._get_relationship(origin_lmm, related_lmm)
            except Relationship.DoesNotExist:
                messages.error(request,
                               f"Relationship {origin_lmm.model.lower()}_{related_lmm.model.lower()}_relationship "
                               f"not exists.")
                return False
        return True

    def seed(self, pk_maps, organization):
        for entry in self.join_records_data:
            # update fields in join_records_data with map
            origin_lmm = LogicModuleModel.objects.get_by_concatenated_model_name(entry.pop("origin_model_name"))
            related_lmm = LogicModuleModel.objects.get_by_concatenated_model_name(entry.pop("related_model_name"))
            entry_data = self.update_field(pk_maps[origin_lmm.endpoint.strip('/')],
                                           [entry],
                                           'record_uuid')
            entry_data = self.update_field(pk_maps[related_lmm.endpoint.strip('/')],
                                           entry_data,
                                           'related_record_uuid')
            # create JoinRecords
            JoinRecord.objects.create(
                relationship=self._get_relationship(origin_lmm, related_lmm),
                organization=organization,
                **entry_data[0]
            )


class SeedBifrost(SeedBase):

    def __init__(self,
                 organization: Organization,
                 workflowleveltypes: List[dict],
                 workflowlevel2s: List[dict],
                 core_users: List[dict]):
        self.organization = organization
        self.workflowleveltypes = deepcopy(workflowleveltypes)
        self.workflowlevel2s = deepcopy(workflowlevel2s)
        self.core_users = deepcopy(core_users)

    def seed(self) -> Tuple[str, dict, dict]:
        """Seed WorkflowLevelTypes, WorkflowLevel1, WorkflowLevel2s."""
        # Seed WorkflowLevelTypes
        wfl_types_map = {}
        for wfl_type_item in self.workflowleveltypes:
            old_wfltypes_uuid = wfl_type_item.pop("uuid")
            wfl_type, _ = WorkflowLevelType.objects.get_or_create(**wfl_type_item)
            wfl_types_map[old_wfltypes_uuid] = wfl_type.uuid

        # Seed WorkflowLevel1
        wfl1, _ = WorkflowLevel1.objects.get_or_create(
            organization=self.organization,
            defaults={"name": "Seed Data prep"}
        )

        # Seed WorkflowLevel2s
        self.update_field(wfl_types_map, self.workflowlevel2s, "type")
        self.update_field({18: wfl1}, self.workflowlevel2s, "workflowlevel1")
        self.update_dates(self.workflowlevel2s, "end_date", 20)
        wfl2_uuid_map = {}
        for wfl2_dict in self.workflowlevel2s:
            wfl2_dict["type_id"] = wfl2_dict.pop("type")
            old_level2_uuid = wfl2_dict.pop("level2_uuid")
            wfl2 = WorkflowLevel2.objects.create(**wfl2_dict)
            wfl2_uuid_map[old_level2_uuid] = str(wfl2.level2_uuid)

        # Seed CoreUsers
        def _get_unique_seeddata_username():
            core_users = CoreUser.objects.filter(username__startswith="SeedData")
            return f"SeedData{core_users.count() + 1}"

        core_user_map = {}
        for core_user_dict in deepcopy(self.core_users):
            old_core_user_uuid = core_user_dict.pop("core_user_uuid")
            core_user_dict["username"] = _get_unique_seeddata_username()
            core_user = CoreUser.objects.create(
                **{**core_user_dict, **{"organization": self.organization}}
            )
            core_user_map[old_core_user_uuid] = str(core_user.core_user_uuid)

        return str(wfl1.level1_uuid), wfl2_uuid_map, core_user_map
