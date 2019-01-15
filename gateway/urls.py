from django.urls import path, re_path
from rest_framework import permissions, routers

from . import views
from . import generator

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="BiFrost API",
        default_version='latest',
        description="Test description",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    generator_class=generator.OpenAPISchemaGenerator
)


router = routers.SimpleRouter()

router.register(r'logicmodule', views.LogicModuleViewSet)

urlpatterns = [
    re_path(r'^(?!admin|oauthuser|health_check|docs|complete|disconnect|oauth'
            r'|static|graphql)(?P<service>[\w\W]+)/(?P<model>[\w\W]+)/'
            r'(?:(?P<pk>\d+)/)?',
            views.APIGatewayView.as_view(), name='api-gateway'),
    re_path(r'^docs/swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
]

urlpatterns += router.urls
