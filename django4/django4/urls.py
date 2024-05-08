"""
URL configuration for django4 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from common import views
## for standalone photos entry app
import readme

urlpatterns = [

    path('', readme.show_readme),
    path('howto/docker/', readme.docker_readme),
    path('admin/', admin.site.urls),

    path('favicon.ico', RedirectView.as_view(url='/static/images/favicon.ico')),
    path('robots.txt', RedirectView.as_view(url='/static/robots.txt')),
##    path('salicicola/', views.salicicola),
##
##
    path('names/', include('names.urls')), 
##    path('bugs/', include('bugs.urls')), 
##    path('photodb/checklist/', include('checklist.urls_flat')), ## checklist_
##    path('photodb/vascular/checklist/', include('checklist.urls_tree')), ## checklist_
##    path('', RedirectView.as_view(url='/photodb/checklist/about/')),
##
path('photodb/', include('photodb.urls')),    
path('photodb/', include('gallery.urls_vascular')),
path('photodb/', include('gallery.urls_gallery')),
path('photodb/', include('photodb.urls_edit')),
##
path('gis/', include('gisapp.urls')),
    
##
    path('servlet/GetImage', views.GetImage),
##    path('servlet/CaptionEditorNew', views.CaptionEditor),

path('photos/', include('photos.urls')),
##path('townmapper/', include('townmapper5.urls')),
##path('herbarium/', include('herbarium.urls')),
##
##path('flora/', include('flora.urls')),
##path('flora/deane/', include('deane96.urls')),
##    
##path('inaturalist/', include('inaturalist.urls')),
##path('LC/', include('LC.urls')),

## no such table: deane96_plantname
##path('flora/deane/', include('deane96.urls')),
]
