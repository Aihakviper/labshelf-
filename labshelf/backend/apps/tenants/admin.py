from django.contrib import admin

from .models import LibraryUser, Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'subscription_plan', 'borrowing_days', 'fine_per_day')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(LibraryUser)
class LibraryUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'role', 'tenant', 'student_id')
    list_filter = ('tenant', 'role')
    search_fields = ('name', 'email', 'student_id')

# Register your models here.
