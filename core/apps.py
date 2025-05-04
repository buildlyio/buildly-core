from __future__ import unicode_literals

from django.apps import AppConfig

ROOT_URLCONF = 'core.urls'


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        import core.signals # noqa
