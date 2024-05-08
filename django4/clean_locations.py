import os, django
print (os.path.abspath('.'))
os.environ['DJANGO_SETTINGS_MODULE']='django4.settings'
django.setup()

import gisapp.models
import common.models

all_locs=common.models.Location.objects.all()
gis_locs = gisapp.models.Locality.objects.all()
print (len(all_locs), all_locs[:10], "common.Location") ## 113
print (len(gis_locs), gis_locs[:10], "common.Location") ## 134
## FIXME: TO FIX 21 orphans

## cleaned and now commented
##for loc in all_locs:
##    gis_locs = gisapp.models.Locality.objects.filter(lcid=loc.lcid)
##    print (loc, gis_locs)
##    if gis_locs:
##        pass
##    else:
##        loc.delete()
##        print ("deleted")
##    
