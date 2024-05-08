from django.urls import path
from . import edit 

## /names/~
urlpatterns = [
    path('edit/name/<int:pnid>/', edit.edit_name_mini, {'template': 'form_namemini.htm'}), ## moved from photodb, template to upper level or to names namespace
    path('delete/name/<int:pnid>/', edit.delete_name_legacy_name),
    path('add/synonym/<int:spid>/', edit.add_syn),
]


