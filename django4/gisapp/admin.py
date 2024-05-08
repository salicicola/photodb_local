from django.contrib import admin
from django.conf import settings # needed if we use the GOOGLE_MAPS_API_KEY from settings
# Grab the Admin Manager that automaticall initializes an OpenLayers map
# for any geometry field using the in Google Mercator projection with OpenStreetMap basedata
from django.contrib.gis.admin import OSMGeoAdmin, GeoModelAdmin
from gisapp.models import *

USE_GOOGLE_TERRAIN_TILES = False
class LocalityAdmin(OSMGeoAdmin):
    """
    
    The class that determines the display of the WorldBorders model
    within the Admin App.
    
    This class uses some sample options and provides a bunch more in commented
    form below to show the various options GeoDjango provides to customize OpenLayers.
    
    For a look at all the GeoDjango options dive into the source code available at:
    
    http://code.djangoproject.com/browser/django/trunk/django/contrib/gis/admin/options.py
    
    """
    # Standard Django Admin Options
    list_display = ('name', 'lcid')
##    list_editable = ('geometry', 'lcid')
    search_fields = ('name',)
    list_per_page = 4
    ordering = ('name',)
    list_filter = ('region','subregion',)
    save_as = True
    list_select_related = True
    fieldsets = (
      ('Country Attributes', 
	{'fields': (('name', 'lcid')), 
	'classes': ('show','extrapretty')}),
      	('Country Codes', {'fields': ('region','subregion',), 'classes': ('collapse',)}),
     ('Area and Coordinates', {'fields': ('area','lat','lon',), 'classes': ('collapse', 'wide')}),
      ('Editable Map View', {'fields': ('geometry',), 'classes': ('show', 'wide')}),
    )

    if USE_GOOGLE_TERRAIN_TILES:
      map_template = 'gis/admin/google.html'
      extra_js = ['http://openstreetmap.org/openlayers/OpenStreetMap.js', 'http://maps.google.com/maps?file=api&amp;v=2&amp;key=%s' % settings.GOOGLE_MAPS_API_KEY]
    else:
      pass # defaults to OSMGeoAdmin presets of OpenStreetMap tiles

    # Default GeoDjango OpenLayers map options
    # Uncomment and modify as desired
    # To learn more about this jargon visit:
    # www.openlayers.org
    
    #default_lon = 0
    #default_lat = 0
    #default_zoom = 4
    #display_wkt = False
    #display_srid = False
    #extra_js = []
    #num_zoom = 18
    #max_zoom = False
    #min_zoom = False
    #units = False
    #max_resolution = False
    #max_extent = False
    #modifiable = True
    #mouse_position = True
    #scale_text = True
    #layerswitcher = True
    scrollable = False
    #admin_media_prefix = settings.ADMIN_MEDIA_PREFIX
    map_width = 400
    map_height = 325
    #map_srid = 4326
    #map_template = 'gis/admin/openlayers.html'
    #openlayers_url = 'http://openlayers.org/api/2.6/OpenLayers.js'
    #wms_url = 'http://labs.metacarta.com/wms/vmap0'
    #wms_layer = 'basic'
    #wms_name = 'OpenLayers WMS'
    #debug = False
    #widget = OpenLayersWidget

# Finally, with these options set now register the model
# associating the Options with the actual model

class USCountyAdmin(OSMGeoAdmin):
    list_display = ('name','state_name','geometry',)
    list_editable = ('geometry', )
    search_fields = ('name', 'state_name')
    list_per_page = 4
    ordering = ('name',)
    list_filter = ('state_name',)
    save_as = True
    list_select_related = True
##    fieldsets = (
##      ('Country Attributes', 
##	{'fields': (('name',)), 
##	'classes': ('show','extrapretty')}),
##      ('Area and Coordinates', {'classes': ('collapse', 'wide')}),
##      ('Editable Map View', {'fields': ('geometry',), 'classes': ('show', 'wide')}),
##    )

class MACountyAdmin(OSMGeoAdmin):
    list_display = ('county','state','geom',)
    list_editable = ('geom', )
    search_fields = ('county', 'state')
    list_per_page = 4
    ordering = ('county',)
    list_filter = ('state',)
    save_as = True
    list_select_related = True
##    fieldsets = (
##      ('Country Attributes', 
##	{'fields': (('name',)), 
##	'classes': ('show','extrapretty')}),
##      ('Area and Coordinates', {'classes': ('collapse', 'wide')}),
##      ('Editable Map View', {'fields': ('geometry',), 'classes': ('show', 'wide')}),
##    )

class OpenspaceAdmin(OSMGeoAdmin):
    list_display = ('site_name',)
##    list_editable = ('geom', )
    search_fields = ('site_name', )
##    list_per_page = 4
##    ordering = ('county',)
##    list_filter = ('state',)
##    save_as = True
##    list_select_related = True

class TDMLocalityAdmin(OSMGeoAdmin):

    list_display = ('name', 'lcid', 'created')
##    list_editable = ('geometry', 'lcid')
    search_fields = ('name',)
    list_per_page = 4
    ordering = ('name',)
    save_as = True
    list_select_related = True

    if USE_GOOGLE_TERRAIN_TILES:
      map_template = 'gis/admin/google.html'
      extra_js = ['http://openstreetmap.org/openlayers/OpenStreetMap.js', 'http://maps.google.com/maps?file=api&amp;v=2&amp;key=%s' % settings.GOOGLE_MAPS_API_KEY]
    else:
      pass # defaults to OSMGeoAdmin presets of OpenStreetMap tiles

admin.site.register(Locality, LocalityAdmin)
admin.site.register(USCounty, USCountyAdmin)
admin.site.register(MACounty, MACountyAdmin)
admin.site.register(Town)
admin.site.register(Openspace, OpenspaceAdmin)

