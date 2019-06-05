from rest_framework import routers

from . import views


router = routers.SimpleRouter()

router.register('joinrecords', views.JoinRecordViewSet)
router.register('models', views.LogicModuleModelViewSet)

urlpatterns = router.urls
