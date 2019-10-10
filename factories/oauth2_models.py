import datetime
from factory import DjangoModelFactory, Faker, SubFactory

from oauth2_provider.models import (
    Application as ApplicationM,
    AccessToken as AccessTokenM)
from .workflow_models import CoreUser


class Application(DjangoModelFactory):
    class Meta:
        model = ApplicationM
        django_get_or_create = ('name',)

    name = 'buildly'
    client_type = ApplicationM.CLIENT_PUBLIC
    authorization_grant_type = ApplicationM.GRANT_PASSWORD
    skip_authorization = True


class AccessToken(DjangoModelFactory):
    class Meta:
        model = AccessTokenM
        django_get_or_create = ('token',)

    token = Faker('ean')
    user = SubFactory(CoreUser)
    application = SubFactory(Application)
    expires = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    scope = 'read write'
