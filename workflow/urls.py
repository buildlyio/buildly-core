from django.urls import path
from rest_framework import routers
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from . import views


router = routers.SimpleRouter()

router.register(r'permissions', views.PermissionViewSet)
router.register(r'coregroups', views.CoreGroupViewSet)
router.register(r'coreuser', views.CoreUserViewSet)
router.register(r'workflowlevel1', views.WorkflowLevel1ViewSet)
router.register(r'workflowlevel2', views.WorkflowLevel2ViewSet)
router.register(r'workflowlevel2sort', views.WorkflowLevel2SortViewSet)
router.register(r'workflowteam', views.WorkflowTeamViewSet)
router.register(r'milestone', views.MilestoneViewSet)
router.register(r'organization', views.OrganizationViewSet)

urlpatterns = [
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True))),
]

urlpatterns += router.urls
