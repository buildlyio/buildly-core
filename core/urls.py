from django.urls import include, path, re_path
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from rest_framework import routers

from core import views
from core.views.web import IndexView, oauth_complete


admin.autodiscover()
admin.site.site_header = 'Buildly Administration'

handler404 = 'core.views.web.handler404'

router = routers.SimpleRouter()

router.register(r'coregroups', views.CoreGroupViewSet)
router.register(r'coreuser', views.CoreUserViewSet)
router.register(r'oauth/accesstokens', views.AccessTokenViewSet)
router.register(r'oauth/applications', views.ApplicationViewSet)
router.register(r'oauth/refreshtokens', views.RefreshTokenViewSet)
router.register(r'organization', views.OrganizationViewSet)
router.register(r'logicmodule', views.LogicModuleViewSet)
router.register(r'partner', views.PartnerViewSet)
router.register(r'stripe', views.StripeViewSet, basename='stripe') 


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('admin/', admin.site.urls),
    path('health_check/', include('health_check.urls')),
    path('datamesh/', include('datamesh.urls')),
    path('', include('gateway.urls')),
    path('', include('workflow.urls')),

    # Auth backend URL's
    path('oauth/', include('oauth2_provider_jwt.urls', namespace='oauth2_provider_jwt')),
    re_path(r'^oauth/complete/(?P<backend>[^/]+)/$', oauth_complete, name='oauth_complete'),
]

urlpatterns += staticfiles_urlpatterns() + router.urls
