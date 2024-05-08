from django.urls import path, re_path
from . import adm_news, admin_lib
from . import views_lib

urlpatterns = [  
	path('adm/new/photos/', adm_news.new_unpublished, {"template":"photodb/adm_new_photos.htm"}), ## default
	path('adm/new/photos/<int:year>/<int:month>/<int:day>', adm_news.new_unpublished, {"template":"photodb/adm_new_photos.htm"}),
	path('adm/new/captions/', adm_news.new_published),
	path('adm/new/captions/<str:date>/', adm_news.new_published), ## with -
	path('missing/thumbs/', admin_lib.make_missing_thumbnails),
        path('indb/<str:phid>/', views_lib.in_db),

]


