from django.contrib import admin
from dashboard.models import Organization
from dashboard.models import Alert
from dashboard.models import Whitelist
from import_export.admin import ImportExportModelAdmin
from import_export import resources

class OrganizationResource(resources.ModelResource):
    class Meta:
        model = Organization
        import_id_fields = ['id',]

class WhitelistResource(resources.ModelResource):
    class Meta:
        model = Whitelist
        import_id_fields = ['id',]

class OrganizationAdmin(ImportExportModelAdmin):
    resource_class = OrganizationResource
    list_display = ('get_domain','get_org','get_category')

class AlertAdmin(admin.ModelAdmin):
    model = Alert
    list_display = ('get_time', 'get_reason', 'get_uri', 'get_raw')

class WhitelistAdmin(ImportExportModelAdmin):
    resource_class = WhitelistResource
    list_display = ('get_pattern',)

admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Alert, AlertAdmin)
admin.site.register(Whitelist, WhitelistAdmin)
