from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AppUser, Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


@admin.register(AppUser)
class AppUserAdmin(UserAdmin):
    list_display = ("username", "full_name", "role", "email", "is_active")
    list_filter = ("role", "is_active", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("Профиль сервиса", {"fields": ("role", "full_name", "phone", "student_code")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Профиль сервиса", {"fields": ("role", "full_name", "phone", "student_code")}),
    )
