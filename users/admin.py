# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Role, Permission, UserActivity

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'name', 'phone', 'status', 'created_at']
    list_filter = ['status', 'roles']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('name', 'email', 'phone', 'cpf', 'birth_date', 'address', 'avatar')}),
        ('Permissões', {'fields': ('status', 'roles', 'permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'created_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'name', 'phone', 'cpf', 'birth_date', 'address', 'status', 'roles', 'permissions'),
        }),
    )
    search_fields = ['name', 'email', 'phone']
    ordering = ['name']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Role)
admin.site.register(Permission)
admin.site.register(UserActivity)