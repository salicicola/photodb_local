from django.urls import path
from . import edit, views, checklist, invasive, get_exotic

## /names/~
urlpatterns = [
path('', views.get_core),
path('vascular/invasive/', invasive.invasive_index, {"template":"names/invasive_index.htm"}),
path('vascular/invasive/<str:show>/', invasive.get_invasive, {"template":"names/invasive.htm"}),

path('vascular/flexible/', checklist.taxa_index, {"mode": "flexible", "template":"names/checklist_nonlegacy_byfams2.htm", "state": ""}), 
path('vascular/flexible/<int:pnid>/', views.get_html, {"state": ""}), 

path('vascular/fixed/',               checklist.taxa_index, {"mode": "fixed", "template":"names/checklist_nonlegacy_byfams.htm"}), 
path('vascular/fixed/<int:fid>/',     checklist.checklist_family, {"template":"names/checklist_nonlegacy_family_new.htm","mode":None}), 
path('vascular/fixed/<int:fid>/all/', checklist.checklist_family, {"template":"names/checklist_nonlegacy_family_new.htm", "mode":"all", "authorized_cnh":True}),

path('edit/name/<int:pnid>/',   edit.edit_name_mini, {'template': 'names/form_namemini.htm'}), 
path('delete/name/<int:pnid>/', edit.delete_name_legacy_name),
path('add/synonym/<int:spid>/', edit.add_syn),

path('xml/<int:pnid>/',             views.get_xml, {"state": ""}), 
path('xml/<int:pnid>/<str:state>/', views.get_xml),

path('vascular/exotic/', get_exotic.exotic),

]



