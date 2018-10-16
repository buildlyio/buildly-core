import requests

from . import exceptions
from . import models as gtm

SWAGGER_LOOKUP_FIELD = 'swagger'
SWAGGER_LOOKUP_FORMAT = 'json'
SWAGGER_LOOKUP_PATH = 'api/docs'


def get_swagger_urls(service: str=None) -> dict:
    """
    Get the endpoint of the service in the database and append
    with the OpenAPI path

    :param service: the name of the service
    :return: the url to fetch the openapi schema
    """
    if service is None:
        modules = gtm.LogicModule.objects.values(
            'name', 'endpoint').all()
    else:
        modules = gtm.LogicModule.objects.values(
            'name', 'endpoint').filter(name__iexact=service)

    if len(modules) == 0 and service is not None:
        msg = 'Service "{}" not found.'.format(service)
        raise exceptions.ServiceDoesNotExist(msg, 404)

    if len(modules) == 0 and service is None:
        msg = 'No service Found.'
        raise exceptions.GatewayError(msg, 404)

    module_urls = dict()
    for module in modules:
        swagger_url = '{}/{}/{}.{}'.format(
            module['endpoint'], SWAGGER_LOOKUP_PATH,
            SWAGGER_LOOKUP_FIELD, SWAGGER_LOOKUP_FORMAT
        )
        module_name = module['name'].lower()
        module_urls[module_name] = swagger_url

    return module_urls


def get_swagger_from_url(api_url: str):
    """
    Get the swagger file of the service at the given url

    :param api_url:
    :return: dictionary representing the swagger definition
    """
    return requests.get(api_url).json()
