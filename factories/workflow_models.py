from factory import DjangoModelFactory, SubFactory

from workflow.models import (
    CoreUser as CoreUserM,
    Organization as OrganizationM,
    WorkflowLevel1 as WorkflowLevel1M,
    WorkflowLevel2 as WorkflowLevel2M,
    WorkflowTeam as WorkflowTeamM,
    WorkflowLevel2Sort as WorkflowLevel2SortM,
    Portfolio as PortfolioM,
    Milestone as MilestoneM,
    Internationalization as InternationalizationM,
)
from .django_models import User, Group


class Organization(DjangoModelFactory):
    class Meta:
        model = OrganizationM
        django_get_or_create = ('name',)

    name = 'Default Organization'


class CoreUser(DjangoModelFactory):
    class Meta:
        model = CoreUserM
        django_get_or_create = ('user',)

    user = SubFactory(User)
    organization = SubFactory(Organization)


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


class Portfolio(DjangoModelFactory):
    class Meta:
        model = PortfolioM

    organization = SubFactory(Organization)


class Milestone(DjangoModelFactory):
    class Meta:
        model = MilestoneM

    organization = SubFactory(Organization)


class Internationalization(DjangoModelFactory):
    class Meta:
        model = InternationalizationM

    language_file = '{"name": "Nome", "gender": "Gênero"}'
