from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from simple_history.admin import SimpleHistoryAdmin

from .models import (CoreUser, CoreGroup, Organization, WorkflowLevel1, WorkflowLevel2,
                     WorkflowLevel2Sort, WorkflowTeam, EmailTemplate, Industry,
                     WorkflowLevelStatus)
from .seeds.admin import OrganizationAdmin


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


class CoreGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'is_global', 'is_org_level', 'is_default', 'permissions')
    display = 'Core Group'
    search_fields = ('name', 'organization__name', )


class CoreUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'organization', 'is_active')
    display = 'Core User'
    list_filter = ('is_staff', 'organization')
    search_fields = ('first_name', 'first_name', 'username', 'title', 'organization__name', )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('title', 'first_name', 'last_name', 'email', 'contact_info', 'organization')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'core_groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'create_date', 'edit_date')}),
    )
    filter_horizontal = ('core_groups', 'user_permissions', )

    def get_fieldsets(self, request, obj=None):

        if not obj:
            return self.add_fieldsets

        fieldsets = super().get_fieldsets(request, obj)

        if not request.user.is_superuser:
            fieldsets[2][1]['fields'] = ('is_active', 'is_staff')
        else:
            fieldsets[2][1]['fields'] = ('is_active', 'is_staff', 'is_superuser', 'core_groups', 'user_permissions')

        return fieldsets


class WorkflowLevel1Admin(SimpleHistoryAdmin):
    list_display = ('name',)
    display = 'Workflow Level1'
    list_filter = ('name',)
    search_fields = ('name',)


class WorkflowLevelStatusAdmin(admin.ModelAdmin):
    list_display = ('order', 'name', 'short_name')


class WorkflowLevel2Admin(SimpleHistoryAdmin):
    list_display = ('name', 'status')
    display = 'Workflow Level1'
    list_filter = ('name', 'status')
    search_fields = ('name',)


class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('organization', 'type')
    display = 'Email Template'


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(WorkflowLevel2, WorkflowLevel2Admin)
admin.site.register(WorkflowLevel1, WorkflowLevel1Admin)
admin.site.register(WorkflowLevel2Sort)
admin.site.register(WorkflowLevelStatus, WorkflowLevelStatusAdmin)
admin.site.register(Industry)
admin.site.register(WorkflowTeam, WorkflowTeamAdmin)
admin.site.register(CoreGroup, CoreGroupAdmin)
admin.site.register(CoreUser, CoreUserAdmin)
admin.site.register(EmailTemplate, EmailTemplateAdmin)
