from factory import DjangoModelFactory

from workflow.models import ROLE_WORKFLOW_ADMIN


class Group(DjangoModelFactory):
    class Meta:
        model = 'auth.Group'
        django_get_or_create = ('name',)

    name = ROLE_WORKFLOW_ADMIN
