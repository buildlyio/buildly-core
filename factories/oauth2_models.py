from factory import DjangoModelFactory

from oauth2_provider.models import Application as ApplicationM


class Application(DjangoModelFactory):
    class Meta:
        model = ApplicationM
        django_get_or_create = ('name',)

    name = 'buildly',
    client_type = ApplicationM.CLIENT_PUBLIC
    authorization_grant_type = ApplicationM.GRANT_PASSWORD
    skip_authorization = True
