from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import (Country, CoreUser, CoreSites,
                     Organization,  WorkflowLevel1,
                     WorkflowLevel2, WorkflowLevel2Sort, WorkflowTeam)

class CountryAdmin(admin.ModelAdmin):
    list_display = ('country', 'code', 'create_date', 'edit_date')
    list_filter = ('country',)


class WorkflowTeamAdmin(admin.ModelAdmin):
    list_display = ('workflow_user', 'budget_limit', 'workflowlevel1',
                    'country')
    display = 'Workflow Team'
    search_fields = ('workflow_user__user__username', 'workflowlevel1__name',
                     'workflow_user__user__last_name', 'country__country')
    list_filter = ('create_date', 'country')


class CoreSitesAdmin(admin.ModelAdmin):
    list_display = ('name',)
    display = 'Core Site'
    list_filter = ('name',)
    search_fields = ('name',)


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'create_date', 'edit_date')
    display = 'Organization'


class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'create_date', 'edit_date')
    display = 'Milestone'


class CoreUserAdmin(admin.ModelAdmin):
    list_display = ('name','organization')
    display = 'Core User'
    list_filter = ('user__is_staff', 'organization')
    search_fields = ('name', 'title')


class WorkflowLevel1Admin(admin.ModelAdmin):
    list_display = ('name',)
    display = 'Workflow Level1'
    list_filter = ('name',)
    search_fields = ('name',)


class WorkflowLevel2Admin(admin.ModelAdmin):
    list_display = ('name',)
    display = 'Workflow Level1'
    list_filter = ('name',)
    search_fields = ('name',)


class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'create_date', 'edit_date')
    display = 'Portfolio'
    list_filter = ('create_date',)
    search_fields = ('name',)


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(WorkflowLevel2, SimpleHistoryAdmin)
admin.site.register(WorkflowLevel1, SimpleHistoryAdmin)
admin.site.register(WorkflowLevel2Sort)
admin.site.register(WorkflowTeam, WorkflowTeamAdmin)
admin.site.register(CoreUser, CoreUserAdmin)

