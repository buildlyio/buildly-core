from rest_framework import routers
from . import views

router = routers.SimpleRouter()

router.register(r'logicmodule', views.LogicModuleViewSet)

urlpatterns = []

urlpatterns += router.urls
