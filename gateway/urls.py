from django.urls import re_path
from rest_framework import routers
from . import views

router = routers.SimpleRouter()

router.register(r'logicmodule', views.LogicModuleViewSet)

urlpatterns = [
    re_path(r'^(?P<service>[a-zA-Z]+)/(?P<model>[a-zA-Z]+)/(?:(?P<pk>\d+)/)?',
            views.APIGatewayView.as_view(),
            name='gateway'),
]

urlpatterns += router.urls
