from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.health_check import views

router = DefaultRouter()
router.register(r'health_check', views.HealthCheck)

urlpatterns = [
    path('', include(router.urls)),
]