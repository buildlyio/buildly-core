import logging
import json
from typing import Any, Dict, Tuple

import requests
import aiohttp
from django.http.request import QueryDict
from bravado_core.spec import Spec
from rest_framework.request import Request
from rest_framework.authentication import get_authorization_header

from . import exceptions
from . import utils

logger = logging.getLogger(__name__)


class BaseSwaggerClient:
    """ Base for client class that is responsible for retrieving data from the service with Swagger spec"""

    def __init__(self, spec: Spec, incoming_request: Request):
        self._spec = spec
        self._in_request = incoming_request
        self._data = dict()

    def request(self, **kwargs):
        raise NotImplementedError()

    def is_valid_for_cache(self) -> bool:
        """ Checks if request is valid for caching operations """
        return self._in_request.method.lower() == 'get' and not self._in_request.query_params

    def prepare_data(self, spec: Spec, **kwargs) -> Tuple[str, str]:
        """ Parse request URL, validates operation, and returns method and URL for outgoing request"""

        # Parse URL kwargs
        pk = kwargs.get('pk')
        model = kwargs.get('model', '').lower()
        path_kwargs = {}
        if kwargs.get('pk') is None:
            path = f'/{model}/'
        else:
            pk_name = 'uuid' if utils.valid_uuid4(pk) else 'id'

            # update path kwargs key name
            # example: {"product_uuid" :"db827034-30bb-4062-ac35-f8c24e8f81ad"}
            path_kwargs = {f'{model}_{pk_name}': pk}

            # create path for retrieving individual data example : /product/{{product_uuid}}/
            path_parameter_name = f'{model}_{pk_name}'
            path = f'/{model}/{{{path_parameter_name}}}/'

        # Check that operation is valid according to spec
        operation = spec.get_op_for_request(self._in_request.method, path)
        if not operation:
            raise exceptions.EndpointNotFound(f'Endpoint not found: {self._in_request.method} {path}')
        method = operation.http_method.lower()
        path_name = operation.path_name

        # Build URL for the operation to request data from the service
        url = spec.api_url.rstrip('/') + path_name
        for k, v in path_kwargs.items():
            url = url.replace(f'{{{k}}}', v)

        return method, url

    def get_request_data(self) -> dict:
        """
        Create the data structure to be used in Swagger request. GET and  DELETE
        requests don't require body, so the data structure will have just
        query parameters if passed to swagger request.
        """
        if self._in_request.content_type == 'application/json':
            return json.dumps(self._in_request.data)

        method = self._in_request.META['REQUEST_METHOD'].lower()
        data = self._in_request.query_params.dict()

        data.pop('aggregate', None)
        data.pop('join', None)

        if method in ['post', 'put', 'patch']:
            query_dict_body = self._in_request.data if hasattr(self._in_request, 'data') else dict()
            body = query_dict_body.dict() if isinstance(query_dict_body, QueryDict) else query_dict_body
            data.update(body)

            # handle uploaded files
            if self._in_request.FILES:
                for key, value in self._in_request.FILES.items():
                    data[key] = {
                        'header': {
                            'Content-Type': value.content_type,
                        },
                        'data': value,
                        'filename': value.name,
                    }

        return data

    def get_headers(self) -> dict:
        """Get data and headers from the incoming request."""
        headers = {
            'Authorization': get_authorization_header(self._in_request).decode('utf-8'),
        }
        if self._in_request.content_type == 'application/json':
            headers['content-type'] = 'application/json'
        return headers


class SwaggerClient(BaseSwaggerClient):
    """ Synchronous implementation of Swagger client using requests lib """

    def request(self, **kwargs) -> Tuple[Any, int, Dict[str, str]]:
        """
        Perform request to the service, use Swagger spec for validating operation
        """

        method, url = self.prepare_data(self._spec, **kwargs)

        # Check request cache if applicable
        if self.is_valid_for_cache() and url in self._data:
            logger.debug(f'Taking data from cache: {url}')
            return self._data[url]

        # Make request to the service
        method = getattr(requests, method)
        try:
            response = method(url,
                              headers=self.get_headers(),
                              params=self._in_request.query_params,
                              data=self.get_request_data(),
                              files=self._in_request.FILES)
        except Exception as e:
            error_msg = (f'An error occurred when redirecting the request to '
                         f'or receiving the response from the service.\n'
                         f'Origin: ({e.__class__.__name__}: {e})')
            raise exceptions.GatewayError(error_msg)

        try:
            content = response.json()
        except ValueError:
            content = response.content
        return_data = (content, response.status_code, response.headers)

        # Cache data if request is cache-valid
        if self.is_valid_for_cache():
            self._data[url] = return_data

        return return_data


class AsyncSwaggerClient(BaseSwaggerClient):
    """ Asynchronous implementation of Swagger client using aiohttp lib """

    async def request(self, **kwargs) -> Tuple[Any, int, Dict[str, str]]:
        method, url = self.prepare_data(self._spec, **kwargs)

        # Check request cache if applicable
        if self.is_valid_for_cache() and url in self._data:
            logger.debug(f'Taking data from cache: {url}')
            return self._data[url]

        # Make request to the service
        async with aiohttp.ClientSession() as session:
            method = getattr(session, method)
            if self._in_request.FILES:
                request_data = self.get_request_data()
                data = aiohttp.FormData()
                for field in request_data:
                    if field == 'file':
                        data.add_field('file', request_data['file']['data'].file)
                    else:
                        data.add_field(field, request_data[field])
            else:
                data = self.get_request_data()

            async with method(url, data=data, headers=self.get_headers()) as response:
                try:
                    content = await response.json()
                except (json.JSONDecodeError, aiohttp.ContentTypeError):
                    content = await response.read()

            return_data = (content, response.status, response.headers)

        # Cache data if request is cache-valid
        if self.is_valid_for_cache():
            self._data[url] = return_data

        return return_data
