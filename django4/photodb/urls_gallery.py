from django.urls import path
from . import views, views_nonlegacy, views_nonvascular
from . import views_filtered, admin_lib ## checklist_wrk, checklist, checklist3, 
 
##/photodb/gallery/ FIXME
urlpatterns = [
    path('gallery/new/checklist/fams/', views_nonlegacy.new_checklist_families, {"template":"photodb/checklist_nonlegacy_byfams.htm"}),
    path('gallery/note/<int:pnid>/', views.show_note),
    path('gallery/mobile/<int:spid>/', views_nonvascular.species_mobile),
    path('gallery/mobile/<int:spid>/<str:imid>/', views_nonvascular.imgview_mobile),
##    path('gallery/new/checklist/new/<int:fid>/', checklist_wrk.checklist_family, {"template":"photodb/checklist_nonlegacy_family_new.htm","mode":None}),
##    path('gallery/new/checklist/new/<int:fid>/all/', checklist.checklist_family, {"template":"photodb/checklist_nonlegacy_family_new.htm", "mode":"all"}),


##    path('gallery/checklist/<str:name>/', checklist.find_taxon),
    path('gallery/new/checklist/<int:fid>/', views_nonlegacy.new_checklist_family, {"template":"photodb/checklist_nonlegacy_family.htm"}),
    path('gallery/new/checklist/all/<int:fid>/', views_nonlegacy.new_checklist_family, {"template":"photodb/checklist_nonlegacy_family_xxx.htm"}),

    path('gallery/simple/<int:pnid>/', views_nonlegacy.view_photo_records, {'legacy':False, "template":"photodb/photos/gallery_index.htm", "public":False}),

    path('gallery/simple/<int:pnid>/<str:county>/', views_filtered.thumview_species_filtered, {"template":"photodb/photos/gallery_index.htm"}),
    path('gallery/new/checklist/bbr/', views_nonlegacy.newflat_checklist_filtered, {"lcid":"MA.BBR", "template":"photodb/checklist_flat_bbr.htm"}),
    path('gallery/new/checklist/grr/', views_nonlegacy.newflat_checklist_filtered, {"lcid":"MA.GRR", "template":"photodb/checklist_flat_bbr.htm"}),

    path('gallery/new/checklist/grr/print/', views_nonlegacy.newflat_checklist_filtered, {"lcid":"MA.GRR", 
    "template":"photodb/checklist_flat_list.htm", "mode":"list"}),
#### should be in gallery
####    path('gallery/view/<int:pnid>/', views_nonlegacy.view_photo_records, {'legacy':False, "template":"photodb/photos/gallery_index.htm", "public":False}), ## changed to False = simple



    ## temp for compatibility, modified views_nonlegacy.view_photo_records
####    path('gallery/view/<int:fid>/<int:pnid>/', views_nonlegacy.view_photo_records, {'legacy':False, "template":"photodb/photos/gallery_index.htm", "public":True}),
####    path('gallery/view/<int:spid>/<str:imid>/', views.image_view, {"legacy":False}),
####
####    path('gallery/view/autoscale/<int:spid>/<str:imid>/', admin_lib.save_autoscale),


    ## ADDED / RESTORED
##    path('gallery/new/checklist/', checklist3.newflat_checklist, {"template": "photodb/checklist_flat.htm", 'filtered':'exotic,cultivated'}),
##    path('gallery/new/checklist/relevant/', checklist3.newflat_checklist, {"template": "photodb/checklist_flat.htm", 'filtered':'exotic,cultivated,no current records'}), ## 3,143
##    path('gallery/new/checklist/minimal/', checklist3.newflat_checklist, {"template": "photodb/checklist_flat.htm", 'filtered':'exotic,cultivated,persistent,no current records'}), ## 2,862
##    path('gallery/new/checklist/missing/', checklist3.newflat_checklist, {"template": "photodb/checklist_flat.htm", 'filtered':'exotic,cultivated,no current records', 'show_missing':False}), ## persistent
 
]

    
####    ##legacy
####	## will use /photodb/vascular/ with "photodb/index_vascular_simplified.htm"
####
####    path('new/checklist/', views_nonlegacy.newflat_checklist),
####    path('new/checklist/fams/', views_nonlegacy.new_checklist_families),
####    path('new/checklist/<int:fid>/', views_nonlegacy.new_checklist_family), ## XXX; new var of omomum not shown
####    path('new/checklist/all/<int:fid>/', views_nonlegacy.new_checklist_family, {"template":"photodb/checklist_nonlegacy_family_all.htm"}),
####
####path('new/checklist/tidmarsh/', views_alpha.newflat_checklist_filtered, {"lcid":"MA.TDM", "template":"photodb/checklist_flat_tidmarsh.htm"}),
####path('new/checklist/bbr/', views_alpha.newflat_checklist_filtered, {"lcid":"MA.BBR", "template":"photodb/checklist_flat_bbr.htm"}),
####
####    path('current/checklist/', views_nonlegacy.newflat_checklist),
####    path('current/checklist/fams/', views_nonlegacy.new_checklist_families),
####    path('current/checklist/<int:fid>/', views_nonlegacy.new_checklist_family),
####
####    
####    path('legacy/checklist/', views_legacy.legacy_checklist),
####    path('legacy/checklist/fams/', views_legacy.legacy_checklist_families),
####    path('legacy/checklist/<int:fid>/', views_legacy.legacy_checklist_family, {"template":"photodb/checklist_legacy_family.htm"}),
####
####    
####	path('legacy/<int:pnid>/', legacy_view.view_photo_records, {'legacy':True, "template":"photodb/photos/gallery_index.htm"}), ##?OK
####	path('view/legacy/<int:pnid>/', legacy_view.view_photo_records, {'legacy':True, "template":"photodb/photos/gallery_index.htm"}), ##?OK ## photodb_thums
####	path('view/legacy/<int:spid>/<str:imid>/', views.image_view, {"legacy":True, "template":"photodb/imageview.htm"}), ## imageview.htm
####	path('view/<int:fid>/<int:spid>/<str:imid>/', views.image_view, {"legacy":True}), ## outdated
####    ## to use cache not tested
####	path('vascular/', views_legacy.index_vascular),
######, {"template": "photodb/index_vascular.htm"}),  ## > should have links legacy/<int:pnid>/ ## @cache_page(None)
####
####
####    path('hierarchic/<int:pnid>/', views_xslt.make_html),
####
####	path('view/<int:spid>/<str:imid>/', views.image_view, {"legacy":False}),
####	path('simple/<int:pnid>/', views_nonlegacy.view_photo_records, {'legacy':False}), ##FIXME
####
####	path('view/<int:pnid>/', views.thums_view),  ## introduced work
####	path('simple/<int:pnid>/', views_nonlegacy.view_photo_records, {'legacy':False}), ##FIXME views_photos
####    ## should be the same as
####    ## path('photos/gallery/<int:pnid>/', legacy_view.view_photo_records, {'legacy':True, "template":"photodb/photos/gallery_index.htm"}), ##FIXME
####	
####	## FIXME
####	path('cache/clear/', views_legacy.clear_index_cache), ##will clear all site-wide cache
####        path('images/index/update/', debugging.name_index_update, {'delete':False}),
####    path('images/index/recreate/', debugging.name_index_update, {'delete':True}),
####    
