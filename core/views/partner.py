from rest_framework import viewsets
from rest_framework.response import Response
from core.serializers import PartnerSerializer
from core.models import Partner


class PartnerViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
