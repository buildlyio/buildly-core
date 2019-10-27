import uuid

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone

from workflow.models import CoreGroup


class LogicModule(models.Model):
    module_uuid = models.CharField(max_length=255, verbose_name='Logic Module UUID', default=uuid.uuid4, unique=True)
    name = models.CharField("Logic Module Name", max_length=255, blank=True)
    description = models.TextField("Description/Notes", max_length=765, null=True, blank=True)
    endpoint = models.CharField(blank=True, null=True, max_length=255)
    endpoint_name = models.CharField(blank=True, null=True, max_length=255)
    docs_endpoint = models.CharField(blank=True, null=True, max_length=255)
    relationships = JSONField(blank=True, null=True)  # TODO: DEPRECATED. It wil be removed when the old data mesh is deleted
    core_groups = models.ManyToManyField(CoreGroup, verbose_name='Logic Module groups', blank=True, related_name='logic_module_set', related_query_name='logic_module')
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "Logic Modules"
        unique_together = (('endpoint', 'endpoint_name'),)

    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = timezone.now()
        self.edit_date = timezone.now()
        super(LogicModule, self).save()

    def __str__(self):
        return str(self.name)
