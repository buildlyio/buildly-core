from django.apps import AppConfig


class WorkflowAppConfig(AppConfig):
    name = 'workflow'

    def ready(self):
        import workflow.signals  # noqa
