import re
from typing import Dict
from uuid import UUID

import datetime
import json
import requests
import logging

from django.db import models
from django.http.request import QueryDict
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
    wfm.Organization: wfv.OrganizationViewSet,
    wfm.WorkflowLevel2Sort: wfv.WorkflowLevel2SortViewSet,
}


def get_swagger_url_by_logic_module(module: LogicModule) -> str:
    """
    Construct the endpoint URL of the service

    :param LogicModule module: the logic module (service)
    :return: OpenAPI schema URL for the logic module
    """
    return '{}/{}/{}.{}'.format(
        module.endpoint, SWAGGER_LOOKUP_PATH,
        SWAGGER_LOOKUP_FIELD, SWAGGER_LOOKUP_FORMAT
    )


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


def get_request_data(request: Request) -> dict:
    """
    Create the data structure to be used in Swagger request. GET and  DELETE
    requests don't required body, so the data structure will have just
    query parameter if passed to swagger request.

    :param rest_framework.Request request: request info
    :return dict: request body structured for PySwagger
    """
    method = request.META['REQUEST_METHOD'].lower()
    data = request.query_params.dict()

    data.pop('aggregate', None)
    data.pop('join', None)

    if method in ['post', 'put', 'patch']:
        qd_body = request.data if hasattr(request, 'data') else dict()
        body = qd_body.dict() if isinstance(qd_body, QueryDict) else qd_body
        data.update(body)

        if request.content_type == 'application/json' and data:
            data = {
                'data': data
            }

        # handle uploaded files
        if request.FILES:
            for key, value in request.FILES.items():
                data[key] = {
                    'header': {
                        'Content-Type': value.content_type,
                    },
                    'data': value,
                    'filename': value.name,
                }

    return data


def is_valid_for_cache(request: Request) -> bool:
    """ Checks if request is valid for caching operations """
    return request.method.lower() == 'get' and not request.query_params


def generate_cache_key(**kwargs):
    """ Generates key for caching from URL keywords args"""
    key = '/{}/{}/'.format(kwargs.get('service'), kwargs.get('model'))
    if 'pk' in kwargs:
        key = '{}{}/'.format(key, kwargs['pk'])
    return key
