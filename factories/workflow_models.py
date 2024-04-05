from factory import DjangoModelFactory, SubFactory

from workflow.models import (
    WorkflowLevel1 as WorkflowLevel1M,
    WorkflowLevel2 as WorkflowLevel2M,
    WorkflowTeam as WorkflowTeamM,
    WorkflowLevel2Sort as WorkflowLevel2SortM,
    Internationalization as InternationalizationM,
    WorkflowLevelType as WorkflowLevelTypeM,
    WorkflowLevelStatus as WorkflowLevelStatusM,
)
from .django_models import Group
from .core_models import CoreUser, Organization


class WorkflowLevelType(DjangoModelFactory):
    class Meta:
        model = WorkflowLevelTypeM


class WorkflowLevelStatus(DjangoModelFactory):
    class Meta:
        model = WorkflowLevelStatusM


class WorkflowLevel1(DjangoModelFactory):
    class Meta:
        model = WorkflowLevel1M

    name = 'Health and Survival for Syrians in Affected Regions'
    organization = SubFactory(Organization)


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
    workflowlevel2_parent = SubFactory(WorkflowLevel2)


class Internationalization(DjangoModelFactory):
    class Meta:
        model = InternationalizationM

    language_file = '{"name": "Nome", "gender": "Gênero"}'
