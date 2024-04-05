from django.contrib import admin

from .models import (
    WorkflowLevel1,
    WorkflowLevel2,
    WorkflowLevel2Sort,
    WorkflowTeam,
    WorkflowLevelStatus,
)


class WorkflowTeamAdmin(admin.ModelAdmin):
    list_display = ('workflow_user', 'workflowlevel1')
    display = 'Workflow Team'
    search_fields = (
        'workflow_user__username',
        'workflowlevel1__name',
        'workflow_user__last_name',
    )
    list_filter = ('create_date',)


class WorkflowLevel1Admin(admin.ModelAdmin):
    list_display = ('name',)
    display = 'Workflow Level1'
    list_filter = ('name',)
    search_fields = ('name',)


class WorkflowLevelStatusAdmin(admin.ModelAdmin):
    list_display = ('order', 'name', 'short_name')


class WorkflowLevel2Admin(admin.ModelAdmin):
    list_display = ('name', 'status')
    display = 'Workflow Level1'
    list_filter = ('name', 'status')
    search_fields = ('name',)


admin.site.register(WorkflowLevel2, WorkflowLevel2Admin)
admin.site.register(WorkflowLevel1, WorkflowLevel1Admin)
admin.site.register(WorkflowLevel2Sort)
admin.site.register(WorkflowLevelStatus, WorkflowLevelStatusAdmin)
admin.site.register(WorkflowTeam, WorkflowTeamAdmin)
