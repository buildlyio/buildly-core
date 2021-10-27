from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from core.models import CoreUser, CoreGroup, CoreSites, EmailTemplate, Industry, LogicModule, Organization, Partner


class LogicModuleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)


class CoreSitesAdmin(admin.ModelAdmin):
    list_display = ('name',)
    display = 'Core Site'
    list_filter = ('name',)
    search_fields = ('name',)


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'create_date', 'edit_date')
    display = 'Organization'


class CoreGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'organization', 'is_global', 'is_org_level', 'is_default', 'permissions')
    display = 'Core Group'
    search_fields = ('name', 'organization__name', )


class CoreUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'organization', 'is_active')
    display = 'Core User'
    list_filter = ('is_staff', 'organization')
    search_fields = ('first_name', 'last_name', 'username', 'title', 'organization__name', )
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


class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('organization', 'type')
    display = 'Email Template'


admin.site.register(LogicModule, LogicModuleAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(CoreGroup, CoreGroupAdmin)
admin.site.register(CoreUser, CoreUserAdmin)
admin.site.register(CoreSites, CoreSitesAdmin)
admin.site.register(EmailTemplate, EmailTemplateAdmin)
admin.site.register(Industry)
admin.site.register(Partner)

