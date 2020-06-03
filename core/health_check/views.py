'''
The view will be a viewset from Django Rest Framework.
Have to overwrite the list method to get the URL from the model and check if it's reachable (return 2xx)
Return a response with the status code 200 and a body like this: {"status": "ok"}

'''

# from health_check.backends import BaseHealthCheckBackend
from rest_framework.decorators import action

from rest_framework import viewsets, status
from rest_framework.response import Response


class HealthCheck(viewsets.GenericViewSet):
    template_name = 'health_check/index.html'

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

    @action(methods=['POST'], detail=False)
    def check_status(self, **kwargs):
        context = super().get_context_data(**kwargs)
        response = self.client.get('/health_check/')
        # self.assertEqual(response.status_code, 200)
        return Response(
            {
                'status':"ok",
            },
            status=status.HTTP_200_OK)
        

  