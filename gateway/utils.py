from . import exceptions
from . import models as gtm

OPENAPI_LOOKUP_FIELD = 'swagger'
OPENAPI_LOOKUP_FORMAT = 'json'
OPENAPI_LOOKUP_PATH = 'api/docs'


def get_openapi_schema_url_by_service(service: str) -> str:
    """
    Get the endpoint of the service in the database and append
    with the OpenAPI path

    :param service: the name of the service
    :return: the url to fetch the openapi schema
    """
    try:
        module_endpoint = gtm.LogicModule.objects.values_list(
            'endpoint', flat=True).get(name__iexact=service)
    except gtm.LogicModule.DoesNotExist:
        msg = 'Service "{}" not found.'.format(service)
        raise exceptions.ServiceDoesNotExist(msg, 404)

    return '{}/{}/{}.{}'.format(module_endpoint, OPENAPI_LOOKUP_PATH,
                                OPENAPI_LOOKUP_FIELD, OPENAPI_LOOKUP_FORMAT)
