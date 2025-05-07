from django.contrib import admin

from .models import SwaggerVersionHistory

class SwaggerVersionHistoryAdmin(admin.ModelAdmin):
    list_display = ('endpoint_name', 'old_version', 'new_version', 'changed_at')
    search_fields = ('endpoint_name',)
    list_filter = ('changed_at',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(SwaggerVersionHistory)