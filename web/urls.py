from django.urls import include, path, re_path
from .views import IndexView, OAuthUserEndpoint, oauth_complete
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()
admin.site.site_header = 'Humanitec Administration'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('admin/', admin.site.urls),
    path('oauthuser/', OAuthUserEndpoint.as_view()),
    path('health_check/', include('health_check.urls')),
    path('datamesh/', include('datamesh.urls')),
    path('', include('gateway.urls')),
    path('', include('workflow.urls')),
    # Auth backend URL's
    path('oauth/',
         include('oauth2_provider_jwt.urls', namespace='oauth2_provider_jwt')),
    re_path(r'^oauth/complete/(?P<backend>[^/]+)/$', oauth_complete,
            name='oauth_complete'),
]

urlpatterns += staticfiles_urlpatterns()
