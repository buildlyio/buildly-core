'''
The model will have two fields:
Name
URL
use the proper Django Fields for each one. Check the reference

'''

from django.db import models
from django.utils import timezone


class HealthCheck(models.Model):
    name = models.CharField("Health_Check Name", blank=True, null=True, max_length=255)
    healthcheck_url = models.CharField(blank = True, null = True, max_length=255, help_text="Link to health check web site")
    health_check_enabled = models.BooleanField('Is health check', default=False)
    create_date = models.DateTimeField(null = True, blank = True)
    edit_date = models.DateTimeField(null = True, blank = True)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "HealthCheck"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = timezone.now()
        self.edit_date = timezone.now()
        super(HealthCheck, self).save(*args, **kwargs)



