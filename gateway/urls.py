from django.urls import path, re_path
from rest_framework import permissions

from . import API_GATEWAY_RESERVED_NAMES
from . import generator
from . import views

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

swagger_info = openapi.Info(
    title="Buildly API",
    default_version='latest',
    description="Buildy Core is a component based gateway for cloud native architectures.",
)

schema_view = get_schema_view(
    swagger_info,
    public=True,
    permission_classes=(permissions.AllowAny,),
    generator_class=generator.OpenAPISchemaGenerator,
)

urlpatterns = [
    # Exclude paths starting with 'oauth/' and other ORM-related endpoints from the gateway
    re_path(
        rf"^(?!oauth/)(?!coregroups/)(?!coreuser/)(?!organization/)(?!logicmodule/)(?!partner/)(?!subscription/)(?!{'|'.join(API_GATEWAY_RESERVED_NAMES)})"  # Reject ORM-related paths and reserved names
        r"async/"
        r"(?P<service>[^/?#]+)/"  # service (timetracking)
        r"(?P<model>[^/?#]+)/?"  # model (timeevent)
        r"(?:(?P<pk>[^?#/]+)/?)?"  # pk (numeric or UUID)
        r"(?:\?(?P<query>[^#]*))?"  # queryparams (?key1=value1&key2=value2)
        r"(?:#(?P<fragment>.*))?",  # fragment (#some-anchor)
        views.APIAsyncGatewayView.as_view(),
        name='api-gateway-async',
    ),
    re_path(
        rf"^(?!oauth/)(?!coregroups/)(?!coreuser/)(?!organization/)(?!logicmodule/)(?!partner/)(?!subscription/)(?!{'|'.join(API_GATEWAY_RESERVED_NAMES)})"  # Reject ORM-related paths and reserved names
        r"(?P<service>[^/?#]+)/"  # service (timetracking)
        r"(?P<model>[^/?#]+)/?"  # model (timeevent)
        r"(?:(?P<pk>[^?#/]+)/?)?"  # pk (numeric or UUID)
        r"(?:\?(?P<query>[^#]*))?"  # queryparams (?key1=value1&key2=value2)
        r"(?:#(?P<fragment>.*))?",  # fragment (#some-anchor)
        views.APIGatewayView.as_view(),
        name='api-gateway',
    ),
    re_path(
        r'^docs/swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-swagger-json',
    ),
    path(
        'docs/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui',
    ),
]