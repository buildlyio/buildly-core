from factory import DjangoModelFactory

from gateway.models import LogicModule as LogicModuleM


class LogicModule(DjangoModelFactory):
    class Meta:
        model = LogicModuleM
        django_get_or_create = ('name',)

    name = 'products'
    endpoint = 'http://products.example.com/'
    relationships = {
        'products': {
            'workflowlevel2_uuid': 'bifrost.WorkflowLevel2'
        }
    }
