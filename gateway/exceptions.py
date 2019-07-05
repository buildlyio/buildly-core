import json


class GatewayError(Exception):
    default_status_code = 500

    def __init__(self, msg, status: int = None):
        content = {'detail': msg}
        self.content = json.dumps(content)
        self.status = status or self.default_status_code
        self.content_type = 'application/json'


class EndpointNotFound(GatewayError):
    default_status_code = 404


class PySwaggerError(GatewayError):
    pass


class RequestValidationError(GatewayError):
    pass


class ServiceDoesNotExist(GatewayError):
    default_status_code = 404


class PermissionDenied(GatewayError):
    default_status_code = 403


class DataMeshError(GatewayError):
    pass
