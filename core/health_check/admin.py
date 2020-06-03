from django.contrib import admin
from core.health_check
from HealthCheck

class HealthcheckConfig(admin.ModelAdmin):
    list_display = ('healthcheck',)
    display = 'Health Check'

admin.site.register(HealthCheck, HealthcheckConfig)
