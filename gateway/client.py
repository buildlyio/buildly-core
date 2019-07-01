from bravado.client import SwaggerClient, CallableOperation
from bravado.http_future import HttpFuture

from .exceptions import EndpointNotFound


class ExtendedSwaggerClient(SwaggerClient):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__also_return_response = kwargs.get('also_return_response', False)

    def call_operation(self, method: str, path: str, **op_kwargs) -> HttpFuture:
        """
        Finds Swagger operation for the passed in request http method and path pattern
        and calls it
        """
        op = self.swagger_spec.get_op_for_request(method, path)

        if not op:
            raise EndpointNotFound(f'Endpoint not found: {method} {path}')

        op = CallableOperation(op, self.__also_return_response)
        return op(**op_kwargs)

