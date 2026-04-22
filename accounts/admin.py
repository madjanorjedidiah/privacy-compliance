from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Membership, Organization, OrgProfile, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Sentinel', {'fields': ('display_name', 'job_title')}),
    )


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'revenue_band', 'employee_band', 'onboarded_at')
    search_fields = ('name', 'slug')


@admin.register(OrgProfile)
class OrgProfileAdmin(admin.ModelAdmin):
    list_display = ('organization', 'cross_border_transfers', 'annual_data_subjects_estimate')


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role', 'is_primary')
    list_filter = ('role',)
