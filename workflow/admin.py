from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from simple_history.admin import SimpleHistoryAdmin

from .models import (CoreUser, CoreGroup, Organization, WorkflowLevel1, WorkflowLevel2,
                     WorkflowLevel2Sort, WorkflowTeam, EmailTemplate)


class WorkflowTeamAdmin(admin.ModelAdmin):
    list_display = ('workflow_user', 'workflowlevel1')
    display = 'Workflow Team'
    search_fields = ('workflow_user__username', 'workflowlevel1__name',
                     'workflow_user__last_name')
    list_filter = ('create_date',)


class CoreSitesAdmin(admin.ModelAdmin):
    list_display = ('name',)
    display = 'Core Site'
    list_filter = ('name',)
    search_fields = ('name',)


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'create_date', 'edit_date')
    display = 'Organization'


class CoreGroupAdmin(admin.ModelAdmin):
    list_display = ('role', 'workflowlevel1', 'workflowlevel2')
    display = 'Core Group'
    list_filter = ('workflowlevel1', 'workflowlevel2',)
    search_fields = ('name', 'workflowlevel1', 'workflowlevel2',)


class CoreUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'organization', 'is_active')
    display = 'Core User'
    list_filter = ('is_staff', 'organization')
    search_fields = ('first_name', 'first_name', 'username', 'title')

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets

        if request.user.is_superuser:
            perm_fields = ('is_active', 'is_staff', 'is_superuser',
                           'groups', 'user_permissions')
        else:
            perm_fields = ('is_active', 'is_staff', 'groups')

        return [(None, {'fields': ('username', 'password')}),
                (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
                (_('Permissions'), {'fields': perm_fields}),
                (_('Important dates'), {'fields':  ('last_login', 'date_joined')})]


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


class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('organization', 'type')
    display = 'Email Template'


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(WorkflowLevel2, SimpleHistoryAdmin)
admin.site.register(WorkflowLevel1, SimpleHistoryAdmin)
admin.site.register(WorkflowLevel2Sort)
admin.site.register(WorkflowTeam, WorkflowTeamAdmin)
admin.site.register(CoreGroup, CoreGroupAdmin)
admin.site.register(CoreUser, CoreUserAdmin)
admin.site.register(EmailTemplate, EmailTemplateAdmin)
