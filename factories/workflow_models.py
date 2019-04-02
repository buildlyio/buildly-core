from django.template.defaultfilters import slugify
from factory import DjangoModelFactory, SubFactory, Faker, lazy_attribute

from workflow.models import (
    CoreUser as CoreUserM,
    CoreGroup as CoreGroupM,
    Organization as OrganizationM,
    WorkflowLevel1 as WorkflowLevel1M,
    WorkflowLevel2 as WorkflowLevel2M,
    WorkflowTeam as WorkflowTeamM,
    WorkflowLevel2Sort as WorkflowLevel2SortM,
    Internationalization as InternationalizationM,
)
from .django_models import Group


class Organization(DjangoModelFactory):
    class Meta:
        model = OrganizationM
        django_get_or_create = ('name',)

    name = 'Default Organization'


class CoreGroup(DjangoModelFactory):

    name = Faker('name')

    class Meta:
        model = CoreGroupM


class CoreUser(DjangoModelFactory):
    class Meta:
        model = CoreUserM
        django_get_or_create = ('username',)

    organization = SubFactory(Organization)
    first_name = 'Homer'
    last_name = 'Simpson'
    username = lazy_attribute(lambda o: slugify(o.first_name + '.' + o.last_name))
    email = lazy_attribute(lambda o: o.username + "@example.com")


User = CoreUser  # for tests incompatibility


class WorkflowLevel1(DjangoModelFactory):
    class Meta:
        model = WorkflowLevel1M

    name = 'Health and Survival for Syrians in Affected Regions'


class WorkflowLevel2(DjangoModelFactory):
    class Meta:
        model = WorkflowLevel2M

    name = 'Help Syrians'
    workflowlevel1 = SubFactory(WorkflowLevel1)


class WorkflowTeam(DjangoModelFactory):
    class Meta:
        model = WorkflowTeamM

    workflow_user = SubFactory(CoreUser)
    workflowlevel1 = SubFactory(WorkflowLevel1)
    role = SubFactory(Group)


class WorkflowLevel2Sort(DjangoModelFactory):
    class Meta:
        model = WorkflowLevel2SortM

    workflowlevel1 = SubFactory(WorkflowLevel1)
    workflowlevel2_parent_id = SubFactory(WorkflowLevel2)


class Internationalization(DjangoModelFactory):
    class Meta:
        model = InternationalizationM

    language_file = '{"name": "Nome", "gender": "Gênero"}'
