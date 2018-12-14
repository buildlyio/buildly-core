from __future__ import absolute_import

from gateway.models import LogicModule
from gateway.serializers import LogicModuleSerializer

from .celery import app


@app.task
def create_module(*args, **kwargs):
    serializer = LogicModuleSerializer(data=args[0])
    serializer.is_valid(raise_exception=True)
    serializer.save()


@app.task
def update_module(*args, **kwargs):
    data = args[0]
    obj_uuid = data['module_uuid']
    instance = LogicModule.objects.get(module_uuid=obj_uuid)
    serializer = LogicModuleSerializer(instance, data=data, partial=False)
    serializer.is_valid(raise_exception=True)
    serializer.save()
