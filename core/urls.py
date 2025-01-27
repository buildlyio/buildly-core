from django.urls import include, path, re_path
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from rest_framework import routers

from core import views
from core.views.homepage import index, oauth_complete

admin.autodiscover()
admin.site.site_header = 'Buildly Administration'

router = routers.SimpleRouter()

router.register(r'coregroups', views.CoreGroupViewSet)
router.register(r'coreuser', views.CoreUserViewSet)
router.register(r'organization', views.OrganizationViewSet)
router.register(r'logicmodule', views.LogicModuleViewSet)
router.register(r'oauth/accesstokens', views.AccessTokenViewSet)
router.register(r'oauth/applications', views.ApplicationViewSet)
router.register(r'oauth/refreshtokens', views.RefreshTokenViewSet)

urlpatterns = [
    path('', index),
    path('admin/', admin.site.urls),
    path('health_check/', include('health_check.urls')),
    path('datamesh/', include('datamesh.urls')),
    path('', include('gateway.urls')),
]

urlpatterns += staticfiles_urlpatterns() + router.urls
