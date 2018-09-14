import os
from django.conf.urls import url, include
from .views import (IndexView, OAuthUserEndpoint)
from django.contrib import admin

admin.autodiscover()
admin.site.site_header = 'Humanitec Administration'

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^admin/', admin.site.urls),
    url(r'^oauthuser', OAuthUserEndpoint.as_view()),
    url(r'^health_check/', include('health_check.urls')),
    url(r'^api/', include('workflow.urls')),
]
