from django.conf.urls import url, include
from .views import (IndexView, OAuthUserEndpoint)
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()
admin.site.site_header = 'Humanitec Administration'

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^admin/', admin.site.urls),
    url(r'^oauthuser', OAuthUserEndpoint.as_view()),
    url(r'^health_check/', include('health_check.urls')),
    url(r'^', include('workflow.urls')),
    url(r'^', include('gateway.urls')),
    # Auth backend URL's
    url('', include('social_django.urls', namespace='social')),
    url(r'^oauth/',
        include('oauth2_provider_jwt.urls', namespace='oauth2_provider_jwt')),
]

urlpatterns += staticfiles_urlpatterns()
