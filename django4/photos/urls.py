from django.urls import path
from . import process, views, tools

urlpatterns = [
    path('rename/', process.process),
    path('rename/<str:ymd>/', process.rename),
    path('update_garmin/<str:ymd>/', process.update_by_garmin),
    path('update_gis/<str:ymd>/', process.update_by_GIS),
    path('', views.index),

    path('entry/', views.entry),   
    path('entry/<int:ymd>/', views.entry_day),  
    path('entry/done/', views.last_committed), 

    path('locations/reset/', tools.update_options), ## updating "photodb/templates/photodb/locations_options" (for MA only)
    path('locations/set/<str:filtering>/', tools.update_options), ## may need to reset after its usage
    path('names/reset/', tools.update_names),       ## updating //scripts/photos/entry/species.xml

]                       
    

