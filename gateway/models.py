from django.db import models


class SwaggerVersionHistory(models.Model):
    endpoint_name = models.CharField(max_length=255)
    old_version = models.CharField(max_length=50, null=True, blank=True)
    new_version = models.CharField(max_length=50)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.endpoint_name}: {self.old_version} -> {self.new_version}"