from django.template.defaultfilters import slugify
from django.utils import timezone
from factory import DjangoModelFactory, SubFactory, Faker, lazy_attribute

from core.models import (
    CoreUser as CoreUserM,
    CoreGroup as CoreGroupM,
    LogicModule as LogicModuleM,
    Organization as OrganizationM,
    Subscription as SubscriptionM,
)


class Organization(DjangoModelFactory):
    class Meta:
        model = OrganizationM
        django_get_or_create = ('name',)

    name = 'Default Organization'


class Subscription(DjangoModelFactory):
    class Meta:
        model = SubscriptionM


class CoreGroup(DjangoModelFactory):

    name = Faker('name')

    class Meta:
        model = CoreGroupM


class CoreUser(DjangoModelFactory):
    class Meta:
        model = CoreUserM
        django_get_or_create = ('username',)

    organization = SubFactory(Organization)
    first_name = Faker('name')
    last_name = Faker('name')
    is_superuser = False
    username = lazy_attribute(lambda o: slugify(o.first_name + '.' + o.last_name))
    email = lazy_attribute(lambda o: o.username + "@example.com")


class CoreSuperUser(DjangoModelFactory):
    class Meta:
        model = CoreUserM
        django_get_or_create = ('username',)

    organization = SubFactory(Organization)
    first_name = Faker('name')
    last_name = Faker('name')
    is_superuser = True
    username = lazy_attribute(lambda o: slugify(o.first_name + '.' + o.last_name))
    email = lazy_attribute(lambda o: o.username + "@example.com")


class LogicModule(DjangoModelFactory):
    class Meta:
        model = LogicModuleM
        django_get_or_create = ('name',)

    name = 'products'
    endpoint = 'http://products.example.com/'
