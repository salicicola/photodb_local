from django.urls import path
from . import edit

## Name edit, delete, add_syn with template name_mini* moved to names namespace 2022-12-28
## adding names left in photoDB gallery
urlpatterns = [  
##  	path('edit/name/<int:pnid>/', edit.edit_name_mini),
	path('identify', edit.identify),
	path('getoptions/<int:fid>/', edit.identify_get_names), ## internally
	path('saveID/', edit.identify_save),
	path('add_genus_species/', edit.add_genus_species),
	path('copyto/', edit.copy_to),
	path('copyto/save/', edit.save_copied),
	path('edit/caption/', edit.CaptionEditor),  ## remove from common XXX
##    path('edit/delete/<int:pnid>/', edit.delete_name_legacy_name),
##    path('add/synonym/<int:spid>/', edit.add_syn),

]


