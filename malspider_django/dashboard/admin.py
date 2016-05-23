from django.contrib import admin
from dashboard.models import Organization
from dashboard.models import Alert
from dashboard.models import Whitelist

class OrganizationAdmin(admin.ModelAdmin):
    model = Organization
    list_display = ('get_domain','get_org','get_category')

class AlertAdmin(admin.ModelAdmin):
    model = Alert
    list_display = ('get_time', 'get_reason', 'get_uri', 'get_raw')

class WhitelistAdmin(admin.ModelAdmin):
    model = Whitelist
    list_display = ('get_pattern',)

admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Alert, AlertAdmin)
admin.site.register(Whitelist, WhitelistAdmin)
