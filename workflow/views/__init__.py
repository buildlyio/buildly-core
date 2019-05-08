from graphene_django.views import GraphQLView

from .coregroup import CoreGroupViewSet  # noqa
from .coreuser import CoreUserViewSet  # noqa
from .i18n import InternationalizationViewSet  # noqa
from .organization import OrganizationViewSet  # noqa
from .workflowlevel1 import WorkflowLevel1ViewSet  # noqa
from .workflowlevel2 import WorkflowLevel2ViewSet, WorkflowLevel2SortViewSet  # noqa
from .workflowteam import WorkflowTeamViewSet  # noqa


# TODO: do we need this?
"""
GraphQL views from Graphene
"""


class DRFAuthenticatedGraphQLView(GraphQLView):
    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super(GraphQLView, cls).as_view(*args, **kwargs)
        return view
