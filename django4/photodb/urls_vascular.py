from django.urls import path
from . import todo, admin_tools, getnews,  adm_news, views_nonlegacy, views_admin

## except vascular/checklist
urlpatterns = [
    path('vascular/todo/', todo.todo_views),
    path('vascular/todo/what/<str:status>/', todo.todo_views),
    path('vascular/todo/when/<str:season>/', todo.todo_views),

    path('vascular/counties/new/', admin_tools.get_new_county_records),

    path('vascular/news/', getnews.make_news),
    path('vascular/news/preview/', adm_news.make_news),
    path('vascular/news/preview/nocache/', adm_news.make_news, {"usecache":False}),
    path('vascular/news/index<int:yyyymmdd>.html', getnews.old_news), 
    path('vascular/admin/latnames/', views_admin.latnames), ## NEW

    path('vascular/gallery/', views_nonlegacy.newflat_checklist, {"template": "photodb/plantgallery_nonlegacy.htm"}),
    path('vascular/latnames/', views_nonlegacy.latnames, {"template": "photodb/latnames.htm", "latnames":True, "cache": False}),
    path('vascular/comnames/', views_nonlegacy.latnames, {"template": "photodb/latnames.htm", "latnames":False, "cache": False}),
    path('vascular/comnames/nocache/', views_nonlegacy.latnames, {"template": "photodb/latnames.htm", "latnames":False, "cache": True}),
    path('vascular/latnames/nocache/', views_nonlegacy.latnames, {"template": "photodb/latnames.htm", "latnames":True, "cache":True}),

    path('vascular/exotic/', views_nonlegacy.flagged, {"kind": "exotic"}),
    path('vascular/cultivated/', views_nonlegacy.flagged, {"kind": "cultivated"}),
    path('vascular/persistent/', views_nonlegacy.flagged, {"kind": "persistent"}),
    path('vascular/notextant/', views_nonlegacy.flagged, {"kind": "no longer extant"}),
    path('vascular/nonnative/<str:kind>/', views_nonlegacy.flagged),
    path('vascular/native/<str:kind>/', views_nonlegacy.flagged, {"template":"photodb/gallery_rare.htm"}),
    path('vascular/news/year/', adm_news.spp_published_year),
    path('vascular/news/year/<int:year>/', adm_news.spp_published_year),
     
]


