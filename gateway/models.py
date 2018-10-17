import uuid

from django.db import models
try:
    from django.utils import timezone
except ImportError:
    from datetime import datetime as timezone


class LogicModule(models.Model):
    module_uuid = models.CharField(max_length=255, verbose_name='Logic Module UUID', default=uuid.uuid4, unique=True)
    name = models.CharField("Logic Module Name", max_length=255, blank=True)
    description = models.TextField("Description/Notes", max_length=765, null=True, blank=True)
    endpoint = models.CharField(blank=True, null=True, max_length=255)
    github_repo = models.CharField(blank=True, null=True, max_length=500)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "Logic Modules"

    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = timezone.now()
        self.edit_date = timezone.now()
        super(LogicModule, self).save()

    def __unicode__(self):
        return self.name
