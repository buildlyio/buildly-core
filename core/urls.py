from django.urls import include, path, re_path
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from rest_framework import routers

from core import views
from core.views.homepage import index
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from core.jwt_utils import CustomTokenObtainPairSerializer
admin.autodiscover()
admin.site.site_header = 'Buildly Administration'

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


router = routers.SimpleRouter()

router.register(r'coregroups', views.CoreGroupViewSet)
router.register(r'coreuser', views.CoreUserViewSet)
router.register(r'organization', views.OrganizationViewSet)
router.register(r'logicmodule', views.LogicModuleViewSet)
router.register(r'partner', views.PartnerViewSet)
router.register(r'subscription', views.SubscriptionViewSet)


urlpatterns = [
    path('', index),
    path('admin/', admin.site.urls),
    path('health_check/', include('health_check.urls')),
    path('datamesh/', include('datamesh.urls')),
    path('', include('gateway.urls')),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # path('oauth/login/', views.LoginView.as_view()),
    # path('oauth/', include(oauth2_urls, namespace='oauth2_provider')),  # OAuth endpoints

]

urlpatterns += staticfiles_urlpatterns() + router.urls
