import os
from django.shortcuts import render
from django.db.models import Q
from .models import *
from .checklist import TCOUNTIES

try:
    from photodb.models import VascularImage
except:
    VascularImage = None
try:
    from townmapper.models import CNHRecord
except:
    CNHRecord = None    

## FIXME: URLs /plants /articles are not available [nearly hardcoding]
if os.path.exists('local'):
    EXTERNAL="http://172.104.19.75/"
    print ("running locally, EXTERNAL = ", EXTERNAL)
else:
    EXTERNAL = ""

MAPSERVER = EXTERNAL

def invasive_index(request, template):
    server = EXTERNAL
    return render (request, template, locals())

def get_invasive(request, template="names/invasive.htm", show='all'):
    print ("running get_invasive filter/show=%s" % show)
    if not VascularImage:
        server=EXTERNAL
        ##images = []
    else:
        server = ""
    if CNHRecord:
        mapserver = ""
    else:
        mapserver = EXTERNAL
    tcounties = TCOUNTIES
    metarecs = SpeciesMeta.objects.filter(species__category='vascular').exclude(invasive__isnull=True).exclude(invasive="")
    print (len(metarecs)) ## 122
    if show == 'notofficial' or show == 'other': ## notofficial
        metarecs = metarecs.exclude(invasive_mipag='Likely Invasive').exclude(invasive_mipag='Invasive').exclude(invasive_mipag='Potentially Invasive')
        print (len(metarecs))
    elif show == 'official' or show == 'mipag': ## need or ||
        metarecs = metarecs.filter(Q(invasive_mipag='Likely Invasive') | Q(invasive_mipag='Invasive') | Q(invasive_mipag='Potentially Invasive'))
        print (len(metarecs))
    elif show == 'official+' or show == 'mipagall': ## need or ||
        metarecs = metarecs.filter(Q(invasive_mipag='Likely Invasive') | Q(invasive_mipag='Invasive') | Q(invasive_mipag='Potentially Invasive') | Q (invasive_mipag ='Do not list at this time'))
        print (len(metarecs))
    elif show == 'invasive' or show=='mipag_invasive': 
        metarecs = metarecs.filter(invasive_mipag='Invasive')
        print (len(metarecs))
    elif show == 'potentially': 
        metarecs = metarecs.filter(invasive_mipag='Potentially Invasive')
        print (len(metarecs))
    elif show == 'likely': 
        metarecs = metarecs.filter(invasive_mipag='Likely Invasive')
        print (len(metarecs))
    elif show == 'rejected': 
        metarecs = metarecs.filter(invasive_mipag='Do not list at this time')
        print (len(metarecs))
    elif show == 'all': 
        ##metarecs = metarecs.filter(invasive_mipag='Likely Invasive')
        print ("unmodified, all", len(metarecs))        
    else:
        print ("unknown filter", show, "will not filter")
        ##metarecs = SpeciesMeta.objects.exclude(invasive__isnull=True).exclude(invasive="").order_by('initial_name')
        pass
    ##metarecs = metarecs.order_by('initial_name')
    metarecs = metarecs.order_by('species__longname')
    print (len(metarecs), "sorted") 
    counter = 0
    for rec in metarecs:
        if rec.species.category == 'vascular':
                counter += 1
                print (counter, rec.species.longname, rec.invasive, "[mipag:", rec.invasive_mipag, "]")
        else:
            print (rec, rec.species.category)
            ##raise Exception()
    return render(request, template, locals())

"""
IPANE:: https://www.invasive.org/weedcd/pdfs/ipane/Alliariapetiolata.pdf
https://www.invasive.org/browse/subthumb.cfm?sub=3005
https://www.fs.usda.gov/database/feis/plants/forb/allpet/all.html
https://plants.usda.gov/home/plantProfile?symbol=ALPE4
http://192.168.1.9:9090/photodb/gallery/view/10101/
http://192.168.1.9:9090/townmapper/spid/10101/
i.e., need species.pnid >>> ipane_pdf, invasive.org.ID, plants_usda.symbol salicicola_note.URL
notes e.g., correctly not considered ovina since it is extremely rare in North America
"""
