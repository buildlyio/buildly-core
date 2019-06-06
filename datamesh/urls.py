from rest_framework import routers

from . import views


router = routers.SimpleRouter()

router.register('joinrecords', views.JoinRecordViewSet)

urlpatterns = router.urls
