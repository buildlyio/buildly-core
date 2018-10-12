from django.contrib import admin

from .models import LogicModule


class LogicModuleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)


admin.site.register(LogicModule, LogicModuleAdmin)
