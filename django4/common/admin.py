from django.contrib import admin
from .models import *

class LocationAdmin(admin.ModelAdmin):
    list_display = ('lcid', 'alias', 'state_abbr', 'county', 'town')
    search_fields = ('lcid', 'town', 'alias', 'public_name', 'long_name')
    list_editable = ('state_abbr', 'county', 'town')
    list_filter = ('state_abbr', 'county')

class BugReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'component', 'version', 'reporter',
                    'actual_user', 'severity', 'hardware', 'OS', 'summary',
                    'description', 'url', 'created', 'modified')
    search_fields = ('summary', 'description')
    list_filter = ('component', 'status')


class TownAdmin(admin.ModelAdmin):
    list_display = ('locID', 'state_abbr', 'county', 'town')
    search_fields = ('locID', 'town', 'county')
    ##list_editable = ('state_abbr', 'county', 'town')
    list_filter = ('county',)


admin.site.register(BugRecord, BugReportAdmin)
admin.site.register(Town, TownAdmin)
admin.site.register(Location, LocationAdmin)
