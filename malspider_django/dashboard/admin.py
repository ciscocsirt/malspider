from django.contrib import admin
from dashboard.models import Organization
from dashboard.models import Alert
from dashboard.models import Whitelist
from dashboard.models import EmailAlert
from import_export.admin import ImportExportModelAdmin
from import_export import resources

class OrganizationResource(resources.ModelResource):
    class Meta:
        model = Organization
        import_id_fields = ['id',]

class AlertResource(resources.ModelResource):
    class Meta:
        model = Alert
        import_id_fields = ['id',]

class WhitelistResource(resources.ModelResource):
    class Meta:
        model = Whitelist
        import_id_fields = ['id',]

class OrganizationAdmin(ImportExportModelAdmin):
    resource_class = OrganizationResource
    list_display = ('get_domain','get_org','get_category')

class AlertAdmin(ImportExportModelAdmin):
    resource_class = AlertResource
    list_display = ('get_time', 'get_reason', 'get_uri', 'get_raw')


class WhitelistAdmin(ImportExportModelAdmin):
    resource_class = WhitelistResource
    list_display = ('get_pattern',)

class EmailAlertAdmin(admin.ModelAdmin):
    model = EmailAlert
    exclude = ('date_added', 'last_email')
    list_display = ('get_recipients', 'get_subject', 'get_frequency')

admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Alert, AlertAdmin)
admin.site.register(Whitelist, WhitelistAdmin)
admin.site.register(EmailAlert, EmailAlertAdmin)
