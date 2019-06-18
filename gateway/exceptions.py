import json


class GatewayError(Exception):
    def __init__(self, msg, status: int = None):
        content = {'detail': msg}
        self.content = json.dumps(content)
        self.status = status
        self.content_type = 'application/json'


class EndpointNotFound(GatewayError):

    def __init__(self, msg='Endpoint not found'):
        super().__init__(msg=msg, status=404)


class PySwaggerError(GatewayError):
    pass


class RequestValidationError(GatewayError):
    pass


class ServiceDoesNotExist(GatewayError):
    pass


class PermissionDenied(GatewayError):
    def __init__(self, msg):
        super(PermissionDenied, self).__init__(msg, 403)


class DataMeshError(GatewayError):
    def __init__(self, msg):
        super().__init__(msg=msg, status=500)
