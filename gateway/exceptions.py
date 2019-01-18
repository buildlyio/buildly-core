import json


class GatewayError(Exception):
    def __init__(self, msg, status: int = None):
        content = {'detail': msg}
        self.content = json.dumps(content)
        self.status = status
        self.content_type = 'application/json'


class EndpointNotFound(Exception):
    pass


class PySwaggerError(GatewayError):
    def __init__(self, msg):
        super(PySwaggerError, self).__init__(msg)


class RequestValidationError(GatewayError):
    def __init__(self, msg, status):
        super(RequestValidationError, self).__init__(msg, status)


class ServiceDoesNotExist(GatewayError):
    def __init__(self, msg, status):
        super(ServiceDoesNotExist, self).__init__(msg, status)
