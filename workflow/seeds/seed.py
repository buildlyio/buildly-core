import json
from copy import deepcopy
from datetime import date, timedelta

import requests
from django.utils.timezone import now


class SeedEnv:
    def __init__(self, headers):
        self.headers = headers


class Seed:
    def __init__(
        self,
        seed_env,
        url,
        pk_maps_map,
        data: list,
        update_fields: dict = None,
        update_dates: dict = None,
        **kwargs
    ):
        self.seed_env = seed_env
        self.url = url
        self.pk_maps_map = pk_maps_map
        self.data = deepcopy(data)
        self.update_fields = update_fields
        self.update_dates = update_dates

    def _update_fields(self):
        """Update every item in data['field_name'] with the help of the map."""
        if not self.update_fields:
            return
        # print("_update_fields")
        for field_name, endpoint in self.update_fields.items():
            # print("-" + field_name)
            # print("-" + endpoint)
            update_map = self.pk_maps_map[endpoint]
            for old_value, new_value in update_map.items():
                # print("--" + str(old_value))
                # print("--" + str(new_value))
                for value_item in self.data:
                    # print("---" + str(value_item))
                    if isinstance(value_item[field_name], list):
                        for i, list_item in enumerate(value_item[field_name]):
                            if list_item == old_value:
                                value_item[field_name][i] = new_value
                    else:
                        if value_item[field_name] == old_value:
                            value_item[field_name] = new_value

    def _update_dates(self):
        """Update the specified dates in the list."""
        if not self.update_dates:
            return
        for item in self.data:
            for date_field_name, days_delta in self.update_dates.items():
                if date_field_name in item.keys():
                    if isinstance(days_delta, dict):
                        new_date = now() + timedelta(**days_delta)
                    else:
                        new_date = now() + timedelta(days=days_delta)
                    item[date_field_name] = new_date.isoformat()

    def _build_map(self, responses):
        pk_map = {}
        for i, entry in enumerate(self.data):
            try:
                pk_map[entry["id"]] = responses[i].json()["id"]
            except KeyError:
                print(f"DONT PRINT ME: {entry}")
        return pk_map

    def perform(self):
        self._update_fields()
        self._update_dates()
        responses = []
        for entry in self.data:
            responses.append(
                requests.post(
                    self.url, data=json.dumps(entry), headers=self.seed_env.headers
                )
            )
            if responses[-1].status_code != 201:
                print(json.dumps(entry))
                print(responses[-1].content)
        return self._build_map(responses)
