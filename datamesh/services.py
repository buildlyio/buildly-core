import logging
import asyncio
from typing import Any, Dict, Generator, Union

from asgiref.sync import sync_to_async
from django.apps import apps
from django.forms.models import model_to_dict

from .models import LogicModuleModel, Relationship, JoinRecord
from .utils import prepare_lookup_kwargs
from .exceptions import DatameshConfigurationError

logger = logging.getLogger(__name__)


class DataMesh:
    """
    Encapsulates aggregation of data from different services (logic modules).
    For each model DataMesh object should be created.
    """

    def __init__(
        self,
        logic_module_endpoint: str,
        model_endpoint: str,
        access_validator: Any = None,
    ):
        self._logic_module_model = LogicModuleModel.objects.get(
            logic_module_endpoint_name=logic_module_endpoint, endpoint=model_endpoint
        )
        self._relationships = self._logic_module_model.get_relationships()
        self._origin_lookup_field = self._logic_module_model.lookup_field_name
        self._access_validator = access_validator
        self._cache = {}

    @classmethod
    async def async_create(cls, logic_module_endpoint, model_endpoint, access_validator=None):
        logic_module_model = await sync_to_async(LogicModuleModel.objects.get)(
            logic_module_endpoint_name=logic_module_endpoint, endpoint=model_endpoint
        )
        instance = cls.__new__(cls)
        instance._logic_module_model = logic_module_model
        instance._relationships = logic_module_model.get_relationships()
        instance._origin_lookup_field = logic_module_model.lookup_field_name
        instance._access_validator = access_validator
        instance._cache = {}
        return instance

    @property
    def related_logic_modules(self) -> list:
        if not hasattr(self, '_related_logic_modules'):
            modules_list = [
                relationship.related_model.logic_module_endpoint_name
                for relationship, _ in self._relationships
                if not relationship.related_model.is_local
            ]
            modules_list_reverse = [
                relationship.origin_model.logic_module_endpoint_name
                for relationship, _ in self._relationships
                if not relationship.origin_model.is_local
            ]
            self._related_logic_modules = set(modules_list + modules_list_reverse)
        return self._related_logic_modules

    def get_related_records_meta(self, origin_pk: Any) -> Generator[tuple, None, None]:
        for relationship, is_forward_lookup in self._relationships:
            join_records = JoinRecord.objects.get_join_records(
                origin_pk, relationship, is_forward_lookup
            )
            if join_records:
                related_model, related_record_field = prepare_lookup_kwargs(
                    is_forward_lookup, relationship, join_records[0]
                )
                for join_record in join_records:
                    params = {
                        'pk': (str(getattr(join_record, related_record_field))),
                        'model': related_model.endpoint.strip('/'),
                        'service': related_model.logic_module_endpoint_name,
                        'pk_name': related_model.lookup_field_name,
                    }
                    yield relationship, params

    async def async_get_related_records_meta(self, origin_pk: Any):
        for relationship, is_forward_lookup in self._relationships:
            join_records = await sync_to_async(JoinRecord.objects.get_join_records)(
                origin_pk, relationship, is_forward_lookup
            )
            if join_records:
                related_model, related_record_field = prepare_lookup_kwargs(
                    is_forward_lookup, relationship, join_records[0]
                )
                for join_record in join_records:
                    params = {
                        'pk': (str(getattr(join_record, related_record_field))),
                        'model': related_model.endpoint.strip('/'),
                        'service': related_model.logic_module_endpoint_name,
                        'pk_name': related_model.lookup_field_name,
                    }
                    yield relationship, params

    def extend_data(self, data: Union[dict, list], client_map: Dict[str, Any]) -> None:
        if isinstance(data, dict):
            self._add_nested_data(data, client_map)
        elif isinstance(data, list):
            for data_item in data:
                self._add_nested_data(data_item, client_map)

    async def async_extend_data(self, data: Union[dict, list], client_map: Dict[str, Any]):
        tasks = []
        if isinstance(data, dict):
            tasks.extend(await self._prepare_tasks(data, client_map))
        elif isinstance(data, list):
            for data_item in data:
                tasks.extend(await self._prepare_tasks(data_item, client_map))
        await asyncio.gather(*tasks)

    def _extend_with_local(
        self, data_item: dict, relationship: Relationship, params: dict
    ) -> None:
        cache_key = f"{params['service']}.{params['model']}.{params['pk']}"
        if cache_key in self._cache:
            data_item[relationship.key].append(self._cache[cache_key])
            return
        try:
            model = apps.get_model(
                app_label=params['service'], model_name=params['model']
            )
        except LookupError as e:
            raise DatameshConfigurationError(f'Data Mesh configuration error: {e}')
        lookup = {params['pk_name']: params['pk']}
        try:
            obj = model.objects.get(**lookup)
        except model.DoesNotExist as e:
            logger.warning(f'{e}, params: {lookup}')
        else:
            if self._access_validator:
                if hasattr(self._access_validator, 'validate') and callable(
                    self._access_validator.validate
                ):
                    self._access_validator.validate(obj)
                else:
                    raise DatameshConfigurationError(f'{"DataMesh Error:Access Validator should have validate method"}')
            obj_dict = model_to_dict(obj)
            data_item[relationship.key].append(obj_dict)
            self._cache[cache_key] = obj_dict

    async def async_extend_with_local(
        self, data_item: dict, relationship: Relationship, params: dict
    ) -> None:
        cache_key = f"{params['service']}.{params['model']}.{params['pk']}"
        if cache_key in self._cache:
            data_item[relationship.key].append(self._cache[cache_key])
            return
        try:
            model = apps.get_model(
                app_label=params['service'], model_name=params['model']
            )
        except LookupError as e:
            raise DatameshConfigurationError(f'Data Mesh configuration error: {e}')
        lookup = {params['pk_name']: params['pk']}
        try:
            obj = await sync_to_async(model.objects.get)(**lookup)
        except model.DoesNotExist as e:
            logger.warning(f'{e}, params: {lookup}')
        else:
            if self._access_validator:
                if hasattr(self._access_validator, 'validate') and callable(
                    self._access_validator.validate
                ):
                    self._access_validator.validate(obj)
                else:
                    raise DatameshConfigurationError(f'{"DataMesh Error:Access Validator should have validate method"}')
            obj_dict = model_to_dict(obj)
            data_item[relationship.key].append(obj_dict)
            self._cache[cache_key] = obj_dict

    def _add_nested_data(self, data_item: dict, client_map: Dict[str, Any]) -> None:
        origin_pk = data_item.get(self._origin_lookup_field)
        if not origin_pk:
            raise DatameshConfigurationError(
                f'DataMesh configuration error: lookup_field_name "{self._origin_lookup_field}" not found in response.'
            )

        for relationship, _ in self._relationships:
            data_item[relationship.key] = []

        for relationship, params in self.get_related_records_meta(origin_pk):
            if relationship.related_model.is_local:
                self._extend_with_local(data_item, relationship, params)
                continue

            params['method'] = 'get'
            client = client_map.get(params['service'])

            if hasattr(client, 'request') and callable(client.request):
                content = client.request(**params)
                if isinstance(content, tuple):
                    if content[1] == 200:
                        content = content[0]
                    else:
                        content = []
                if isinstance(content, dict):
                    data_item[relationship.key].append(dict(content))
                else:
                    logger.error(
                        f'No response data for join record (request params: {params})'
                    )
            else:
                raise DatameshConfigurationError(f'{"DataMesh Error: Client should have request method"}')

    async def _prepare_tasks(self, data_item: dict, client_map: Dict[str, Any]) -> list:
        tasks = []

        origin_pk = data_item.get(self._origin_lookup_field)
        if not origin_pk:
            raise KeyError(
                f'DataMesh Error: lookup_field_name "{self._origin_lookup_field}" not found in response.'
            )

        for relationship, _ in self._relationships:
            data_item[relationship.key] = []

        # Use async generator for related records meta
        async for relationship, params in self.async_get_related_records_meta(origin_pk):
            if relationship.related_model.is_local:
                tasks.append(self.async_extend_with_local(data_item, relationship, params))
                continue

            params['method'] = 'get'
            client = client_map.get(params['service'])
            tasks.append(
                self._extend_content(client, data_item[relationship.key], **params)
            )

        return tasks

    async def _extend_content(
        self, client: Any, placeholder: list, **request_kwargs
    ) -> None:
        content = await client.request(**request_kwargs)
        if isinstance(content, tuple):
            content = content[0]
        if isinstance(content, dict):
            placeholder.append(dict(content))
        else:
            logger.error(
                f'No response data for join record (request params: {request_kwargs})'
            )

    def fetch_datamesh_relationship(self):
        relationship_list = []
        request_param = {}

        for relationship, is_forward_lookup in self._relationships:

            if is_forward_lookup:
                related_model = relationship.related_model
            else:
                related_model = relationship.origin_model

            relationship_list.append(relationship.key)

            params = {
                'pk': None,
                'model': related_model.endpoint.strip('/'),
                'service': related_model.logic_module_endpoint_name,
                'related_model_pk_name': relationship.related_model.lookup_field_name,
                'origin_model_pk_name': relationship.origin_model.lookup_field_name,

                'fk_field_name': relationship.fk_field_name,
                'is_forward_lookup': is_forward_lookup,
                'is_local': relationship.related_model.is_local
            }

            request_param[relationship.key] = params
        return relationship_list, request_param