from django.contrib import admin

from .models import Framework, Jurisdiction, Requirement, RequirementMapping


@admin.register(Jurisdiction)
class JurisdictionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'region', 'authority')
    search_fields = ('name', 'code')


@admin.register(Framework)
class FrameworkAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'jurisdiction', 'enacted_year')
    list_filter = ('jurisdiction',)
    search_fields = ('short_name', 'long_name', 'code')


@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = ('code', 'framework', 'category', 'severity_weight')
    list_filter = ('framework', 'category')
    search_fields = ('code', 'title')


@admin.register(RequirementMapping)
class RequirementMappingAdmin(admin.ModelAdmin):
    list_display = ('source', 'target', 'equivalence')
    list_filter = ('equivalence',)
