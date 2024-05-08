from django.urls import path, re_path
from . import views, update_lcid_gps, new_kml_import, convert

## @ /gis/~
urlpatterns = [
    re_path('location/import/kml/(MA.[A-Za-z]+.[A-Za-z_]+.\d+)', new_kml_import.import_kml),
    re_path('location/import/kml/(MA.[A-Za-z]+.[A-Za-z_]+)', new_kml_import.import_kml),

    path('update/photos/', update_lcid_gps.update_gpx),  

    path('convert/waypoints/kml/<str:basename>/', convert.waypoints_kml),
    path('convert/track/kml/<str:basename>/', convert.track_kml),
    path('convert/kml/shape/<str:basename>/', convert.toshape),

    path('download/waypoints/kml/<str:basename>/', convert.waypoints_kml, {"download":True}),
    path('download/track/kml/<str:basename>/', convert.track_kml, {"download":True}),
    path('download/kml/shape/<str:basename>/', convert.toshape, {"download":True}),

    
    path('find/<str:imid>/', views.get_location),

    path('find/<str:lat>/<str:lon>/', views.get_location),

    path('', views.gis_index),
]                       

print ("loaded gisapp.urls with urlpatterns : ", str(urlpatterns))


