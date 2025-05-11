from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from core.models import CoreUser, CoreGroup, CoreSites, EmailTemplate, Industry, LogicModule, Organization, OrganizationType, Partner, \
    Coupon, Referral, Subscription


class LogicModuleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)


class CoreSitesAdmin(admin.ModelAdmin):
    list_display = ('name',)
    display = 'Core Site'
    list_filter = ('name',)
    search_fields = ('name',)


class OrganizationTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    display = 'Organization Type'


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization_type', 'create_date', 'edit_date')
    display = 'Organization'


class CoreGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'organization', 'is_global', 'is_org_level', 'is_default', 'permissions')
    display = 'Core Group'
    search_fields = ('name', 'organization__name')


class CoreUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'organization', 'is_active', 'user_type', 'survey_status','create_date')
    display = 'Core User'
    list_filter = ('is_staff', 'organization')
    search_fields = ('first_name', 'last_name', 'username', 'title', 'organization__name', )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('title', 'first_name', 'last_name', 'email', 'contact_info', 'organization', 'user_type', 'survey_status')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'core_groups', 'user_permissions')}),
        (_('Preferences'), {'fields': ('email_preferences', 'push_preferences')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'create_date', 'edit_date')}),
    )
    filter_horizontal = ('core_groups', 'user_permissions')

    def get_fieldsets(self, request, obj=None):

        if not obj:
            return self.add_fieldsets

        fieldsets = super().get_fieldsets(request, obj)

        if not request.user.is_superuser:
            fieldsets[2][1]['fields'] = ('is_active', 'is_staff')
        else:
            fieldsets[2][1]['fields'] = (
                'is_active',
                'is_staff',
                'is_superuser',
                'core_groups',
                'user_permissions',
            )

        return fieldsets


class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('organization', 'type')
    display = 'Email Template'


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'percent_off', 'duration', 'max_redemptions', 'active')
    list_filter = ('active', 'duration')
    search_fields = ('code', 'name')


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'organization', 'coupon', 'active')
    list_filter = ('active', 'organization', 'coupon')
    search_fields = ('code', 'name', 'organization__name', 'coupon__name')


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'stripe_subscription_id', 'subscription_start_date', 'subscription_end_date')
    list_filter = ('stripe_subscription_id', 'organization')
    search_fields = ('user__username', 'organization__name')
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'organization')


admin.site.register(LogicModule, LogicModuleAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrganizationType, OrganizationTypeAdmin)
admin.site.register(CoreGroup, CoreGroupAdmin)
admin.site.register(CoreUser, CoreUserAdmin)
admin.site.register(CoreSites, CoreSitesAdmin)
admin.site.register(EmailTemplate, EmailTemplateAdmin)
admin.site.register(Industry)
admin.site.register(Partner)
admin.site.register(Subscription, SubscriptionAdmin)

