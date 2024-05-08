import sys
from django.urls import path, include   ##, re_path
from . import views, view_map, views_legacy, views_nonlegacy, animals3, views_nonvascular
from . import flora2, flora3 ## flora, 

urlpatterns = [
	path('', views.front_page, {"template":"photodb/front_page_pub.htm"}),
        path('photos/<str:imid>/', views.allphotos_fromimid),
##	path('', include('photodb.checklist_urls')),
	path('', include('photodb.urls_gallery')),
	path('', include('photodb.urls_vascular')),
############ XXX #############	path('tidmarsh/', include ('photodb.urls_tidmarsh')),
############ XXX #############	path('search/', include ('photodb.urls_search')),

	path('acmemap/<str:gps>/', view_map.acmemap_gps),
	path('plantgallery/', views_nonlegacy.newflat_checklist, {"template": "photodb/plantgallery_nonlegacy.htm"}),

        ## admin and edit
        path('', include('photodb.urls_admin')), ## needs adm_news, admin_lib
        path('', include('photodb.urls_edit')), ## needs edit
        
	##animals + non vascular : views_legacy, views_nonlegacy, animals3, views_nonvascular
        path('animals/', views_nonlegacy.animals_index, {'template': 'photodb/animals_new.htm'}),
        path('animals/odonata/', animals3.three_level, {"template": "photodb/gallery_thums3.htm"}),
        path('animals/birds/', animals3.three_level, {"template": "photodb/gallery_thums3.htm", "upper":11950}),   
	## temp for compatibility, modified views_nonlegacy.view_photo_records
	path('nonvascular/admin/', views_legacy.index_legacy_simplified, {'category': 'nonvascular', 'template':'photodb/index_not_vascular_simplified.htm'}), ## 
	path('nonvascular/', views_nonvascular.index_legacy_simplified, {'template': 'photodb/index_notvascular_simple.htm', 'mobile': False}),    
	path('nonvascular/mobile/', views_nonvascular.index_legacy_simplified, {'template': 'photodb/index_notvascular_mobile.htm', 'mobile': True}), ##
        path('flora/<str:locId>', flora2.get_plantlist),
        ##path('flora/<str:locId>', flora.plant_list),
        path('flora/', flora2.index),
  path('regional/<str:locId>/', flora3.get_checklist),  
        
]
## entry* module
try:
    from . import entry, entry_test
    urlpatterns.extend( [
    path('entry/from/<str:fname>', entry.save_from),
    path('entry/legacy/', entry_test.entry_form, {"template": "photodb/entry_legacy.htm"}),
    path('entry/new/', entry_test.entry_form, {"template": "photodb/entry_new.htm"}),
    path('entry/legacy/<str:fname>',  entry_test.send_image),
    path('entry/legacy/delete/<str:fid>/', entry_test.move_deleted_photo),
    path('entry/savephoto', entry_test.save_photo_records),
    path('delete/<str:imid>/', entry_test.move_deleted_photo),
    path('entry/single/', entry_test.entry_one), ## supply tomcat path to image as path=
    path('entry/species/update/', entry.create_species_xml),
    ## new patch
    path('entry/getgid/<int:pnid>/', entry.get_gid),
    path('entry/getfid/<int:pnid>/', entry.get_fid),
] )
except:
    print (sys.exc_info())
    print ("cannot use entry modules")
    raise

print ("end of photodb.urls", urlpatterns)

##edit, views_nonlegacy, views_legacy, animals3, checklist, views_filtered, views_admin, views_nonvascular
##from . import admin_lib, admin_tools, news, getnews, adm_news
##from . import todo, view_map, checklist3, checklist_wrk, checklist_xml
    
##from . import views, views_nonlegacy
##from . import views_legacy, admin_lib, views_files, debugging   ## to clean
##from . import search, tdm_mapper, tidmarsh, tidmarsh_entry, mapper3, animals3
####entry, edit, views, views_legacy, views_xslt, views_photos, admin_export, debugging, views_files ##, admin_images2
####from . import entry_test, temp, legacy_view, search
####from . import admin_lib

##	path('gallery/', include ('photodb.urls_gallery')),  ## mostly thumbviews and imageviews, and gallery/vascular
##	##FIXME	path('export/', include ('photodb.urls_export')),
##	path('add/synonym/<int:spid>/', edit.add_syn),

## vascular/

##path('checklist/vascular/',  include('photodb.checklist_urls')),


## to django4 public, too

###path('checklist/', checklist3.newflat_checklist, {"template": "photodb/checklist_flat_new.htm", 'filtered':'exotic,cultivated'}),
## path('checklist/about/', checklist_wrk.about),
## path('checklist/famsnew/', checklist_xml.get_families, {"template":"photodb/checklist_nonlegacy_byfams2.htm"}),  ## ## NEW !!!
## path('checklist/fams/', views_nonlegacy.new_checklist_families, {"template":"photodb/checklist_nonlegacy_byfams.htm"}),  ## added fams 2022-08-24
## path('checklist/fams/old/', views_nonlegacy.new_checklist_families, {"template":"photodb/checklist_nonlegacy_byfams.htm"}),  ## added fams 2022-08-24


##path('checklist/', checklist_wrk.newflat_checklist, {"template": "photodb/checklist_flat_new.htm", 'filtered':'exotic,cultivated'}),
##    path('checklist/relevant/', checklist_wrk.newflat_checklist, {"template": "photodb/checklist_flat_new.htm", 'filtered':'exotic,cultivated,no current records'}), ## 3,143
##    path('checklist/minimal/', checklist_wrk.newflat_checklist, {"template": "photodb/checklist_flat_new.htm", 'filtered':'exotic,cultivated,persistent,no current records'}), ## 2,862
##    path('checklist/legacy/', checklist_wrk.newflat_checklist, {"template": "photodb/checklist_flat_new.htm", 'filtered':'exotic,cultivated,legacy', 'show_missing':False}), ## yet tod
##    path('checklist/missing/', checklist_wrk.newflat_checklist, {"template": "photodb/checklist_flat_new.htm", 'filtered':'exotic,cultivated,no current records', 'show_missing':False}), ## persistent


## = path('vascular/checklist/fams/', views_nonlegacy.new_checklist_families, {"template":"photodb/checklist_nonlegacy_byfams.htm"}),
##newer urls
##    path('checklist/<int:fid>/', checklist_wrk.checklist_family, {"template":"photodb/checklist_nonlegacy_family_new.htm","mode":None}), ## authorized_cnh default
##    path('checklist/<int:fid>/all/', checklist_wrk.checklist_family, {"template":"photodb/checklist_nonlegacy_family_new.htm", "mode":"all", "authorized_cnh":True}),
##path('checklist/<str:name>/', checklist.find_taxon),
##path('checklist/<str:genus>/<str:species>/', checklist.find_species),

##  path('varia/', views_legacy.index_legacy_simplified, {'category': 'varia', 'template':'photodb/index_not_vascular_simplified.htm'}),
##    path('check/captions/', views.check_captions), ## 
##    path('check/captions/animals/', views.check_captions, {"category":"animals"}), ## 
##    path('gallery/images/index/recreate/', views.name_index_update, {'delete':True}), ## was in debugging
    ## fixed bug no county filter
##path('gallery/view/<int:pnid>/<str:county>/', views_filtered.thumview_species_filtered, {"template":"photodb/photos/gallery_index.htm"}),
    
 ## 3,172 [persistent]   [no current records] XXX  
##    path('gallery/new/checklist/tidmarsh/', views_nonlegacy.newflat_checklist_filtered, {"lcid":"MA.TDM", "template":"photodb/checklist_flat_tidmarsh.htm"}),
##    path('gallery/new/checklist/bbr/', views_nonlegacy.newflat_checklist_filtered, {"lcid":"MA.BBR", "template":"photodb/checklist_flat_bbr.htm"}),
##
##    ## admin functions
##    path('debug/files/', views_files.index),
##    path('debug/uncommitted/', views_files.uncommitted), ## from debugging.test1
##    path('debug/uncommitted/<int:year>/', views_files.uncommitted), ##
##    path('debug/files/<int:year>/', debugging.test2),

