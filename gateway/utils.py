from uuid import UUID

import datetime
import re
import json
import requests
import logging

from rest_framework.request import Request

from workflow import views as wfv
from workflow import models as wfm

from . import exceptions
from .models import LogicModule


SWAGGER_LOOKUP_FIELD = 'swagger'
SWAGGER_LOOKUP_FORMAT = 'json'
SWAGGER_LOOKUP_PATH = 'docs'
MODEL_VIEWSETS_DICT = {
    wfm.WorkflowTeam: wfv.WorkflowTeamViewSet,
    wfm.WorkflowLevel2: wfv.WorkflowLevel2ViewSet,
    wfm.WorkflowLevel1: wfv.WorkflowLevel1ViewSet,
    wfm.CoreUser: wfv.CoreUserViewSet,
    wfm.Group: wfv.GroupViewSet,
    wfm.Organization: wfv.OrganizationViewSet,
    wfm.Milestone: wfv.MilestoneViewSet,
    wfm.WorkflowLevel2Sort: wfv.WorkflowLevel2SortViewSet,
}


def get_swagger_urls(service: str = None) -> dict:
    """
    Get the endpoint of the service in the database and append
    with the OpenAPI path

    :param str service: the name of the service
    :return: dict
             Key-value pair with service name and OpenAPI schema URL of it
    """
    if service is None:
        modules = LogicModule.objects.values(
            'name', 'endpoint').all()
    else:
        modules = LogicModule.objects.values(
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
        # for handling pyswagger.primitives
        if hasattr(obj, 'to_json'):
            return obj.to_json()
        return json.JSONEncoder.default(self, obj)
