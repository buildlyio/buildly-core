import json
import logging
import string
from copy import deepcopy
from datetime import timedelta

import requests
from django.conf import settings
from django.contrib import messages
from django.utils.timezone import now

from oauth2_provider_jwt.utils import generate_payload, encode_jwt

from datamesh.models import LogicModuleModel, Relationship, JoinRecord
from gateway.models import LogicModule
from workflow.models import CoreUser
from workflow.seeds.utils import _update_value_data

logger = logging.getLogger(__name__)


class SeedEnv:

    def __init__(self, user: CoreUser, organization_uuid: string, pk_maps: dict = {}):
        self.headers = self._create_headers(user, organization_uuid)
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


class Seed:

    def __init__(
        self,
        seed_env,
        seed_data: dict,
        **kwargs
    ):
        self.seed_env = seed_env
        self.seed_data = deepcopy(seed_data)

    def _update_fields(self, update_fields_dict: dict, post_data: list):
        """Update every item in post_data['field_name'] with the help of the map."""
        for field_name, endpoint in update_fields_dict.items():
            update_map = self.seed_env.pk_maps[endpoint]
            for old_value, new_value in update_map.items():
                for value_item in post_data:
                    if isinstance(value_item[field_name], list):
                        for i, list_item in enumerate(value_item[field_name]):
                            if list_item == old_value:
                                value_item[field_name][i] = new_value
                    else:
                        if value_item[field_name] == old_value:
                            value_item[field_name] = new_value

    @staticmethod
    def _update_dates(update_dates_dict: dict, post_data: list):
        """Update the specified dates in the list."""
        for item in post_data:
            for date_field_name, days_delta in update_dates_dict.items():
                if date_field_name in item.keys():
                    if isinstance(days_delta, dict):
                        new_date = now() + timedelta(**days_delta)
                    else:
                        new_date = now() + timedelta(days=days_delta)
                    item[date_field_name] = new_date.isoformat()

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

    def seed_logic_modules(self):
        for logic_module_name in self.seed_data.keys():
            logic_module = LogicModule.objects.get(name=logic_module_name)
            for model_endpoint in self.seed_data[logic_module_name].keys():
                post_data = self.seed_data[logic_module_name][model_endpoint]["data"]
                self._update_fields(
                    self.seed_data[logic_module_name][model_endpoint].get("update_fields", {}),
                    post_data
                )
                self._update_dates(
                    self.seed_data[logic_module_name][model_endpoint].get("update_dates", {}),
                    post_data
                )
                responses = self.post_create_requests(
                    f"{logic_module.endpoint}/{model_endpoint}/",
                    post_data
                )
                self.seed_env.pk_maps[model_endpoint] = self._build_map(responses, post_data)


class SeedDataMesh:

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
            entry_data = _update_value_data(pk_maps[origin_lmm.endpoint.strip('/')],
                                            [entry],
                                            'record_uuid')
            entry_data = _update_value_data(pk_maps[related_lmm.endpoint.strip('/')],
                                            entry_data,
                                            'related_record_uuid')
            # create JoinRecords
            JoinRecord.objects.create(
                relationship=self._get_relationship(origin_lmm, related_lmm),
                organization=organization,
                **entry_data[0]
            )
