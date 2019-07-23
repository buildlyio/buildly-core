import logging
import asyncio
from typing import Any, Dict, Generator, Union

from .models import LogicModuleModel, JoinRecord
from .utils import prepare_lookup_kwargs

logger = logging.getLogger(__name__)


class DataMesh:
    """
    Encapsulates aggregation of data from different services (logic modules).
    For each model DataMesh object should be created.
    """

    def __init__(self, logic_module_endpoint: str, model_endpoint: str):
        self._logic_module_model = LogicModuleModel.objects.get(logic_module_endpoint_name=logic_module_endpoint,
                                                                endpoint=model_endpoint)
        self._relationships = self._logic_module_model.get_relationships()
        self._origin_lookup_field = self._logic_module_model.lookup_field_name

    @property
    def related_logic_modules(self) -> list:
        """
        Gets a list of logic modules names that are related to current model
        """
        if not hasattr(self, '_related_logic_modules'):
            modules_list = [relationship.related_model.logic_module_endpoint_name
                            for relationship, _ in self._relationships]
            self._related_logic_modules = list(dict.fromkeys(modules_list))
        return self._related_logic_modules

    def get_related_records_meta(self, origin_pk: Any) -> Generator[int, None, None]:
        """
        Gets list of related records' META-data that is used for retrieving data for each of these records
        """
        for relationship, is_forward_lookup in self._relationships:
            join_records = JoinRecord.objects.get_join_records(origin_pk, relationship, is_forward_lookup)
            if join_records:
                related_model, related_record_field = prepare_lookup_kwargs(
                    is_forward_lookup, relationship, join_records[0])

                for join_record in join_records:

                    yield {
                        'relationship_key': relationship.key,
                        'params': {
                            'pk': (str(getattr(join_record, related_record_field))),
                            'model': related_model.endpoint.strip('/'),
                            'service': related_model.logic_module_endpoint_name,
                        }
                    }

    def extend_data(self, data: Union[dict, list], client_map: Dict[str, Any]) -> None:
        """
        Extends given data according to this DataMesh's relationships.
        For getting extended data it uses a client objects (one for each related service).
        """
        if isinstance(data, dict):
            # one-object JSON
            self._add_nested_data(data, client_map)
        elif isinstance(data, list):
            # many-objects JSON
            for data_item in data:
                self._add_nested_data(data_item, client_map)

    def _add_nested_data(self, data_item: dict, client_map: Dict[str, Any]) -> None:
        """
        Nest data retrieved from related services.
        """
        origin_pk = data_item.get(self._origin_lookup_field)
        if not origin_pk:
            raise KeyError(
                f'DataMesh Error: lookup_field_name "{self._origin_lookup_field}" not found in response.'
            )

        for relationship, _ in self._relationships:
            data_item[relationship.key] = []

        for meta in self.get_related_records_meta(origin_pk):
            request_kwargs = meta['params']
            request_kwargs['method'] = 'get'
            relationship_key = meta['relationship_key']

            client = client_map.get(meta['params']['service'])

            if hasattr(client, 'request') and callable(client.request):
                content = client.request(**request_kwargs)
                if isinstance(content, tuple):  # assume that response body is the first returned value
                    content = content[0]
                if isinstance(content, dict):
                    data_item[relationship_key].append(dict(content))
                else:
                    logger.error(f'No response data for join record (request params: {request_kwargs})')
            else:
                raise AttributeError(f'DataMesh Error: Client should have request method')

    async def async_extend_data(self, data: Union[dict, list], client_map: Dict[str, Any]):
        """
        Async aggregation logic
        """
        tasks = []
        if isinstance(data, dict):
            # detailed view
            tasks.extend(await self._prepare_tasks(data, client_map))
        elif isinstance(data, list):
            # list view
            for data_item in data:
                tasks.extend(await self._prepare_tasks(data_item, client_map))
        await asyncio.gather(*tasks)

    async def _prepare_tasks(self, data_item: dict, client_map: Dict[str, Any]) -> list:
        """ Creates a list of coroutines for extending data from other services asynchronously """
        tasks = []

        origin_pk = data_item.get(self._origin_lookup_field)
        if not origin_pk:
            raise KeyError(
                f'DataMesh Error: lookup_field_name "{self._origin_lookup_field}" not found in response.'
            )

        for relationship, _ in self._relationships:
            data_item[relationship.key] = []

        for meta in self.get_related_records_meta(origin_pk):
            request_kwargs = meta['params']
            request_kwargs['method'] = 'get'
            relationship_key = meta['relationship_key']

            client = client_map.get(meta['params']['service'])

            tasks.append(self._extend_content(client, data_item[relationship_key], **request_kwargs))

        return tasks

    async def _extend_content(self, client: Any, placeholder: list, **request_kwargs) -> None:
        """ Performs data request and extends data with received data """

        content = await client.request(**request_kwargs)
        if isinstance(content, tuple):  # assume that response body is the first returned value
            content = content[0]
        if isinstance(content, dict):
            placeholder.append(dict(content))
        else:
            logger.error(f'No response data for join record (request params: {request_kwargs})')