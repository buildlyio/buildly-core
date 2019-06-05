from rest_framework import mixins
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from datamesh.models import JoinRecord, LogicModuleModel
from datamesh.serializers import JoinRecordSerializer, LogicModuleModelSerializer


class LogicModuleModelViewSet(ModelViewSet):

    queryset = LogicModuleModel.objects.all()
    serializer_class = LogicModuleModelSerializer


class JoinRecordViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        GenericViewSet):

    queryset = JoinRecord.objects.all()
    serializer_class = JoinRecordSerializer
