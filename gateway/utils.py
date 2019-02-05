from uuid import UUID

import datetime
import re
import json
import requests

from pyswagger.primitives.comm import PrimJSONEncoder


from . import exceptions
from . import models as gtm

SWAGGER_LOOKUP_FIELD = 'swagger'
SWAGGER_LOOKUP_FORMAT = 'json'
SWAGGER_LOOKUP_PATH = 'docs'


def get_swagger_urls(service: str = None) -> dict:
    """
    Get the endpoint of the service in the database and append
    with the OpenAPI path

    :param str service: the name of the service
    :return: dict
             Key-value pair with service name and OpenAPI schema URL of it
    """
    if service is None:
        modules = gtm.LogicModule.objects.values(
            'name', 'endpoint').all()
    else:
        modules = gtm.LogicModule.objects.values(
            'name', 'endpoint').filter(name__istartswith=service)

    if len(modules) == 0 and service is not None:
        msg = 'Service "{}" not found.'.format(service)
        raise exceptions.ServiceDoesNotExist(msg, 404)

    module_urls = dict()
    for module in modules:
        swagger_url = '{}/{}/{}.{}'.format(
            module['endpoint'], SWAGGER_LOOKUP_PATH,
            SWAGGER_LOOKUP_FIELD, SWAGGER_LOOKUP_FORMAT
        )
        module_name = re.sub('_service$', '', module['name'].lower())
        module_urls[module_name] = swagger_url

    return module_urls


def get_swagger_from_url(api_url: str):
    """
    Get the swagger file of the service at the given url

    :param api_url:
    :return: dictionary representing the swagger definition
    """
    try:
        return requests.get(api_url).json()
    except requests.exceptions.ConnectionError as error:
        raise requests.exceptions.ConnectionError(
            f'Please, check that {api_url} is accessible.') from error


def obj_to_json_default_handler(obj):
    """
    JSON doesn't have a default datetime type, so this is why Python can't
    handle it automatically. So you need to make the datetime into a string.
    """
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return obj.__str__()
    raise TypeError("Object of type '%s' is not handled and JSON serialized "
                    "yet" % obj.__class__.__name__)


def json_dump(obj):
    """Serialize ``obj`` to a JSON formatted ``str``."""
    return json.dumps(obj,
                      cls=PrimJSONEncoder,
                      default=obj_to_json_default_handler)
