from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from graphene_django.views import GraphQLView
from web import views as views_web
from . import views

router = routers.SimpleRouter()

router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'coreuser', views.CoreUserViewSet)
router.register(r'organization', views.OrganizationViewSet)
router.register(r'country', views.CountryViewSet)
router.register(r'workflowlevel1', views.WorkflowLevel1ViewSet)
router.register(r'workflowlevel2', views.WorkflowLevel2ViewSet)
router.register(r'workflowlevel2sort', views.WorkflowLevel2SortViewSet)
router.register(r'workflowteam', views.WorkflowTeamViewSet)
router.register(r'milestone', views.MilestoneViewSet)
router.register(r'organization', views.OrganizationViewSet)

urlpatterns = [
    url(r'^docs/', include_docs_urls(title='BiFrost API')),
    url(r'^graphql', GraphQLView.as_view(graphiql=True)),
    url(r'^oauthuser', views_web.OAuthUserEndpoint.as_view())
]

urlpatterns += router.urls
