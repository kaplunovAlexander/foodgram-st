from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


class UserAdmin(BaseUserAdmin):
    model = User

    fieldsets = (
        (None, {'fields': ('username',)}),
        (_('Личная информация'), {
            'fields': (
                'first_name',
                'last_name',
                'email',
            )
        }),
        (_('Права доступа'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        (_('Важные даты'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'first_name', 'last_name', 'email',
                'is_staff', 'is_active',
            ),
        }),
    )
    list_display = (
        'username', 'first_name', 'last_name', 'email',
        'is_active', 'is_staff', 'date_joined'
    )
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)


admin.site.register(User, UserAdmin)
