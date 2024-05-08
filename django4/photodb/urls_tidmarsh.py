from django.urls import path, re_path
from . import tidmarsh, tidmarsh_admin, tdm_mapper, views_nonlegacy, views, tidmarsh_entry, tidmarsh_admin
##from . import  views_legacy, mapper3, 

urlpatterns = [  
    path('', tidmarsh.tidmarsh_index, {"template":"photodb/tidmarsh/tidmarsh_index.htm"}),      	
    path('checklist/', tidmarsh.checklist, {"template": "photodb/tidmarsh/checklist_vascular_tidmarsh.htm"}),
    path('gallery/view/<int:spid>/<str:imid>/', views.image_view, {"legacy":False, "lcid_starts":"MA.TDM"}),
    path('gallery/view/<int:pnid>/', views_nonlegacy.view_photo_records, {'legacy':False, "template":"photodb/photos/gallery_index.htm", "public":True, "lcid_starts":"MA.TDM"}),
    path('map/<int:spid>/', tdm_mapper.large_dot_map_new),
    path('note/<int:spid>/', tidmarsh_admin.edit_note),
    path('inaturalist/', tidmarsh.tidmarsh_inaturalist), ## use photodb/CACHE/tidmarsh_inaturalist.htm

    path('inaturalist/make/', tidmarsh_admin.create_tdm_inat), ### RECREATING XXX
    
    path('map/', tdm_mapper.large_dot_map_single), ## in GET: lat, lon, plantname
    path('nonvascular/', tidmarsh.getnonvascular, {'template': 'photodb/tidmarsh/gallery_nonvascular.htm'}), ##corrected
    path('vertebrates/', tidmarsh.vertebrates, {"template": "photodb/tidmarsh/vertebrates.htm"}), ##corrected
    path('invertebrates/', tidmarsh.invertebrates, {"template": "photodb/tidmarsh/invertebrates.htm"}),  ##corrected
    path('varia/', tidmarsh.getvaria, {'template': 'photodb/tidmarsh/varia.htm'}), ##corrected
    path('search/', tidmarsh.tidmarsh_search, {"template": "photodb/tidmarsh/search_photos.htm"}), ##corrected
    path('introducing/', tidmarsh.introducing),
    path('unwanted/', tidmarsh.unwanted),
    path('map/bbox/', tidmarsh.tidmarsh_bbox),
	path('view/<int:spid>/<str:imid>/', tidmarsh.show_image, {'template': 'photodb/imgview.htm'}),

##    path('animals/', tidmarsh.allcat, {'category': 'animals'}),
    
    
##    path('monitor/', tidmarsh.monitor_index, {"template":"photodb/tidmarsh_monitor.htm"}),
##    path('map/preview/', mapper3.tdm_raster_map_single), ## in GET: lat, lon, plantname
##    path('entry/', tidmarsh_entry.tdm_entry_form_new, {"template":"photodb/tdm_entry_form_new.htm"}), ## new TO TEST
##    path('map/preview/plant/(\d+)/', mapper3.tdm_raster_map_simple),
##    path('map/preview/41.0/-70.0/', mapper3.tdm_raster_map_single), ## XXX re_path ne rabotaet, set lat lon defaults
##    re_path('map/preview/([0-9]+\.?[0-9]+)/([0-9]+\.?[0-9]+)/', mapper3.tdm_raster_map_single), ## was 41 70 for Tidmarsh 'map/preview/(41.\d+)/(-70.\d+)/$'
##    path('map/preview/(41.\d+)/(-70.\d+)/(\w+)/', mapper3.tdm_raster_map_single), ## was 41 70 for Tidmarsh
##
    path('entry/verify/(\w+)/(\d+)/', tidmarsh_entry.set_attribute, {"action": "verified"}),
    path('entry/unverify/(\w+)/(\d+)/', tidmarsh_entry.set_attribute, {"action": "unverify"}),
    path('entry/delete/(\w+)/(\d+)/', tidmarsh_entry.set_attribute, {"action": "delete"}),
    path('entry/restore/(\w+)/(\d+)/', tidmarsh_entry.set_attribute, {"action": "restore"}),
    path('entry/', tidmarsh_entry.question),
    path('entry/(\w+)/(\d+)/', tidmarsh_entry.question), ## edit existed one, uid, rid
    path('entry/save/', tidmarsh_entry.save_entry),
    path('entry/view/(\w+)/(\d+)/', tidmarsh_entry.view_record), ## uid, rid
    path('entry/awc/', tidmarsh_entry.entry_awc, {"mobile": False}),
    path('entry/awc/m/', tidmarsh_entry.entry_awc, {"mobile": True}),
  
]


