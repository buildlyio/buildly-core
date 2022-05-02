import re
from typing import Dict
from uuid import UUID

import datetime
import json
import requests
import logging

from django.db import models
from rest_framework.request import Request

from workflow import views as wfv
from workflow import models as wfm

from . import exceptions
from core.models import CoreUser, LogicModule, Organization
from core.views import CoreUserViewSet, OrganizationViewSet

SWAGGER_LOOKUP_FIELD = 'swagger'
SWAGGER_LOOKUP_FORMAT = 'json'
SWAGGER_LOOKUP_PATH = 'docs'
MODEL_VIEWSETS_DICT = {
    wfm.WorkflowTeam: wfv.WorkflowTeamViewSet,
    wfm.WorkflowLevel2: wfv.WorkflowLevel2ViewSet,
    wfm.WorkflowLevel1: wfv.WorkflowLevel1ViewSet,
    CoreUser: CoreUserViewSet,
    Organization: OrganizationViewSet,
    wfm.WorkflowLevel2Sort: wfv.WorkflowLevel2SortViewSet,
}


def get_swagger_url_by_logic_module(module: LogicModule) -> str:
    """
    Construct the endpoint URL of the service

    :param LogicModule module: the logic module (service)
    :return: OpenAPI schema URL for the logic module
    """
    swagger_lookup = module.docs_endpoint if module.docs_endpoint else SWAGGER_LOOKUP_PATH
    return '{}/{}/{}.{}'.format(module.endpoint, swagger_lookup, SWAGGER_LOOKUP_FIELD, SWAGGER_LOOKUP_FORMAT)


def get_swagger_urls() -> Dict[str, str]:
    """
    Get the endpoint of the service in the database and append
    with the OpenAPI path

    :return: dict
             Key-value pair with service name and OpenAPI schema URL of it
    """
    modules = LogicModule.objects.all()

    module_urls = dict()
    for module in modules:
        swagger_url = get_swagger_url_by_logic_module(module)
        module_urls[module.endpoint_name] = swagger_url

    return module_urls


def get_swagger_from_url(api_url: str):
    """
    Get the swagger file of the service at the given url
    :param api_url:
    :return: dictionary representing the swagger definition
    """
    try:
        return requests.get(api_url)
    except requests.exceptions.ConnectTimeout as error:
        raise TimeoutError(
            f'Connection timed out. Please, check that {api_url} is accessible.') from error
    except requests.exceptions.ConnectionError as error:
        raise ConnectionError(
            f'Please, check that {api_url} is accessible.') from error


def validate_object_access(request: Request, obj):
    """
    Raise a PermissionDenied-Exception in case the User has no access to
    the object or return None.

    :param Request request: incoming request
    :param obj: the object to be validated
    """
    # instantiate ViewSet with action for has_obj_permission
    model = obj.__class__
    try:
        viewset = MODEL_VIEWSETS_DICT[model]()
    except KeyError:
        logging.critical(f'{model} needs to be added to MODEL_VIEWSETS_DICT')
        raise exceptions.GatewayError(
            msg=f'{model} not defined for object access lookup.')
    else:
        viewset.request = request
        viewset.check_object_permissions(request, obj)


class ObjectAccessValidator:
    """
    Create an instance of this class to validate access to an object
    """

    def __init__(self, request: Request):
        self._request = request

    def validate(self, obj):
        return validate_object_access(self._request, obj)


class GatewayJSONEncoder(json.JSONEncoder):
    """
    JSON encoder for API Gateway
    """

    def default(self, obj):
        """
        JSON doesn't have a default datetime and UUID type, so this is why
        Python can't handle it automatically. So you need to make the
        datetime and/or UUID into a string.
        """
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, models.Model):  # for handling objects in M2M-fields
            return obj.pk
        # for handling pyswagger.primitives
        if hasattr(obj, 'to_json'):
            return obj.to_json()
        return json.JSONEncoder.default(self, obj)


def valid_uuid4(uuid_string):
    uuid4hex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z',  # noqa
                          re.I)
    match = uuid4hex.match(uuid_string)
    return bool(match)
