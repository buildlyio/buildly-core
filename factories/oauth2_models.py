import datetime
from factory.django import DjangoModelFactory
from factory import SubFactory, Faker, post_generation

from oauth2_provider.models import (
    Application as ApplicationM,
    AccessToken as AccessTokenM,
    RefreshToken as RefreshTokenM,
)
from core.models import CoreUser


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


class RefreshToken(DjangoModelFactory):
    class Meta:
        model = RefreshTokenM
        django_get_or_create = ('token',)

    token = Faker('ean')
    user = SubFactory(CoreUser)
    application = SubFactory(Application)

    @post_generation
    def access_token(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            self.access_token = extracted
        else:
            self.access_token = AccessToken(application=self.application)
        self.application = self.access_token.application
