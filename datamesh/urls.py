from rest_framework import routers

from . import views


router = routers.SimpleRouter()

router.register('joinrecords', views.JoinRecordViewSet)
router.register('logicmodulemodels', views.LogicModuleModelViewSet)
router.register('relationships', views.RelationshipViewSet)

urlpatterns = router.urls
