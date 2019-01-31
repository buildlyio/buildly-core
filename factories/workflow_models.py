from factory import DjangoModelFactory, LazyAttribute, SubFactory

from workflow.models import (
    CoreUser as CoreUserM,
    Organization as OrganizationM
)


class Organization(DjangoModelFactory):
    class Meta:
        model = OrganizationM

    name = 'Default Organization'


class CoreUser(DjangoModelFactory):
    class Meta:
        model = CoreUserM
        django_get_or_create = ('user',)

    name = LazyAttribute(lambda o: o.user.first_name + " " + o.user.last_name)
    organization = SubFactory(Organization)
