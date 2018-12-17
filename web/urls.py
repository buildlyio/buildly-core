from django.urls import include, path
from .views import IndexView, OAuthUserEndpoint
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()
admin.site.site_header = 'Humanitec Administration'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('admin/', admin.site.urls),
    path('oauthuser/', OAuthUserEndpoint.as_view()),
    path('health_check/', include('health_check.urls')),
    path('', include('gateway.urls')),
    path('', include('workflow.urls')),
    # Auth backend URL's
    path('', include('social_django.urls', namespace='social')),
    path('oauth/',
         include('oauth2_provider_jwt.urls', namespace='oauth2_provider_jwt')),
]

urlpatterns += staticfiles_urlpatterns()
