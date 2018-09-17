from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class CustomUserAdmin(UserAdmin):
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets

        if request.user.is_superuser:
            perm_fields = ('is_active', 'is_staff', 'is_superuser',
                           'groups', 'user_permissions')
        else:
            perm_fields = ('is_active', 'is_staff', 'groups')

        return [(None, {'fields': ('username', 'password')}),
                (_('Personal info'), {'fields': ('first_name', 'last_name',
                                                 'email')}),
                (_('Permissions'), {'fields': perm_fields}),
                (_('Important dates'), {'fields':  ('last_login',
                                                    'date_joined')})]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
