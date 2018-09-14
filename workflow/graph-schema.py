from graphene_django import DjangoObjectType
import graphene
from workflow import models as wfm

#GraphQL CoreUser
class CoreUser(DjangoObjectType):
    class Meta:
        model = wfm.CoreUser


#GraphQL WORKFLOWLEVEL1
class WorkflowLevel1(DjangoObjectType):
    class Meta:
        model = wfm.WorkflowLevel1


# GraphQL WORKFLOWLEVEL2
class WorkflowLevel2(DjangoObjectType):
    class Meta:
        model = wfm.WorkflowLevel2


# GraphQL Milestone
class Milestone(DjangoObjectType):
    class Meta:
        model = wfm.Milestone


# GraphQL Currency
class Country(DjangoObjectType):
    class Meta:
        model = wfm.Country



#Query each class
class Query(graphene.ObjectType):
    users = graphene.List(CoreUser)
    workflowlevel1s = graphene.List(WorkflowLevel1)
    workflowlevel2s = graphene.List(WorkflowLevel2)

    @graphene.resolve_only_args
    def resolve_users(self):
        return wfm.CoreUser.objects.all()

    @graphene.resolve_only_args
    def resolve_milestone(self):
        return wfm.Milestone.objects.all()

    @graphene.resolve_only_args
    def resolve_country(self):
        return wfm.Country.objects.all()

    @graphene.resolve_only_args
    def resolve_workflowlevel1s(self):
        return wfm.WorkflowLevel1.objects.all()

    @graphene.resolve_only_args
    def resolve_workflowlevel2s(self):
        return wfm.WorkflowLevel2.objects.all()


#export schema
schema = graphene.Schema(query=Query)

