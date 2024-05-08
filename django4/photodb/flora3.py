import xml.dom.minidom, os, datetime, sys, time
from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from common.models import *
from names.models import *
from photodb.models import *

VERSION = "0.4 alpha (2023-10-28)"

class FakeMeta:
    def __init__(self, pnid):
        self.introduced="NA"
        self.invasive="NA"
        self.spid=pnid
    


def index(request):
    return render(request, 'photodb/flora_index.htm', {'version':VERSION})

def get_names(recs, public=False):
    names = {}
    for rec in recs:
        plant = rec.plant
        if plant in names:
            names[plant.longname]["imids"].append(rec.imid)
        else:
            try:
                meta = SpeciesMeta.objects.get(spid=plant.pnid)
                names[plant.longname] = {"upper": plant.upper.upper.upper, "family": plant.upper.upper, "plant": plant, "meta":meta, "imids":[rec.imid]}
            except:
                ##names[plant.longname] = {"upper": None, "family": None, "plant": plant, "meta":{}, "imids":[rec.imid]}
                names[plant.longname] = {"upper": None, "family": None, "plant": plant, "meta":FakeMeta(rec.plant.pnid), "imids":[rec.imid]}
                print ("error:", plant.longname, names[plant.longname])
                ##raise
                ## XXX in http://localhost:9090/photodb/regional/WM/
                ## XXX still line 56, in get_checklist : 'dict' object has no attribute 'introduced'
    return names    


def get_checklist(request, public=True, locId="MA.MSF"):
    if locId == "MA.MSF" or locId == "MSF":
        cache = "flora/CACHE/MSF.html"
        if os.path.exists(cache):
            html = open(cache).read()
            return HttpResponse(html)
    elif locId == "WM":
        locId = "MA.Nrf.Ded.202001011"
        cache = "flora/CACHE/WM.html"
        if os.path.exists(cache):
            html = open(cache).read()
            return HttpResponse(html)
    if 'MSF' in locId:
        image = "/static/myles_coverage.jpg"
    else:
        image = ""
    version = VERSION
    loc_name,  photo_records = loc_name, recs = get_records(locId)
    print (loc_name)
    print (len(photo_records))
    names = get_names(recs, public=False)
    print ("names", len(names), type(names))
    today = "today"
    introduced = 0
    invasive = 0
    for longname in names: ## key
        print (longname, names[longname]["meta"])
        if names[longname]["meta"].introduced:
            introduced += 1
            if names[longname]["meta"].invasive:
                invasive += 1
    UGIDS = [301319, 301314, 301309, 301307, 301308, 301299]
    tree = []
    for ugid in UGIDS: 
        higher = Name.objects.get(pk=ugid)
        print ("do higher", higher)
        higher.latname = higher.latname.replace('_', ' ')
        group = {"higher": higher, "fams": [], "taxa": 0, "images":0} 
        tree.append( group )
        ##print (group)
        for fam in Name.objects.filter(upper=higher).order_by('latname'):
            family = {"fam": fam, "genera": [], "images":0, "taxa": 0, "species":{}}
            group["fams"].append(family)
            for gen in Name.objects.filter(upper=fam).filter(level='genus').order_by('latname'):
                genus = {"genus": gen, "species":[], "images":0, "taxa": 0}
            ## ignoring genera?
            for rec in  photo_records:
                sp_ = rec.plant
                gen_ = sp_.upper
                fam_ =  gen_.upper
                
                if fam_ == fam:
                    group["images"] += 1
                    family["images"] += 1
                    existed = family["species"].get(sp_.longname)
                    if existed:
                        existed["images"].append(rec.imid)
                        if rec.nr > 0 and rec.nr < 100:
                            existed["pubimages"].append(rec.imid)
                        ##print (existed)
                    else:
                        try:
                            family["species"][sp_.longname] = {"species": sp_, "meta": SpeciesMeta.objects.get(spid=sp_.pnid), "images": [rec.imid]}
                        except:
                            family["species"][sp_.longname] = {"species": sp_, "meta": FakeMeta(sp_.pnid), "images": [rec.imid]}
                        if rec.nr > 0 and rec.nr < 100:
                            try:
                                family["species"][sp_.longname] = {"species": sp_, "meta": SpeciesMeta.objects.get(spid=sp_.pnid), "images": [rec.imid], "pubimages": [rec.imid]}
                            except:
                                family["species"][sp_.longname] = {"species": sp_, "meta": FakeMeta(sp_.pnid), "images": [rec.imid], "pubimages": [rec.imid]}
                        else:
                            try:
                                family["species"][sp_.longname] = {"species": sp_, "meta": SpeciesMeta.objects.get(spid=sp_.pnid), "images": [rec.imid], "pubimages": []}
                            except:
                                family["species"][sp_.longname] = {"species": sp_, "meta":  FakeMeta(sp_.pnid), "images": [rec.imid], "pubimages": []}

            ##xxx = dict(sorted(family["species"].items()))
            ##print (xxx)
            family["species"] = dict(sorted(family["species"].items()))
    generated = timezone.datetime.now()
    return render(request, 'photodb/flora_public.htm', locals())
                
##    upper = [
##        Name.objects.get(pnid=301319),
##        Name.objects.get(pnid=301314),
##        Name.objects.get(pnid=301309),
##        Name.objects.get(pnid=301308),
##        Name.objects.get(pnid=301307),
##        Name.objects.get(pnid=301299),
##    ]
##    fams = []
##    for longname in names:
##        fam = names[longname]["family"]
##        if not fam in fams:
##            fams.append(fam)
##    tree = []
##    for upper_pnid in [301319, 301314, 301309, 301308, 301307, 301299]:
##        upper = Name.objects.get(pnid=upper_pnid)
##        fams = Name.objects.filter(upper=upper)
##        tree.append([upper.latname, {"fams": fams}])
##    
##    print (tree)
    
    

def get_records(lcid_start):
    locs = Location.objects.filter(lcid__startswith=lcid_start)
    loc_names = {}
    loc_name = "" #!
    for loc in locs:
        if loc.public_name:
            locname_ = loc.public_name.split(',')[0]
            if locname_ in loc_names:
                loc_names[locname_] += 1
            else:
                loc_names[locname_] = 1
    print (loc_names)
    counter = 0
    for locname_ in loc_names:
        if loc_names[locname_] > counter:
            counter = loc_names[locname_]
            loc_name = locname_
            print (counter, loc_name)
        else:
            print ("ignore", locname_, loc_names[locname_])
    print (loc_name)
    photo_records = VascularImage.objects.filter(locality__in = locs)
    print (len(photo_records), "recs")
    output = (loc_name,  photo_records)
    
    return output

@login_required(login_url='/admin/login/')    
def get_plantlist(request, locId):
    print ("running get_plantlist for locId %s" % locId)
    if not "." in locId:
        if locId=="WM":
            locId = "MA.Nrf.Ded.202001011"
        else:
            locId = "MA.%s" % locId
    print ("final locId %s" % locId)        
    loc_name, recs = get_records(locId)
    return simple_list(request, recs, loc_name)

## from flora.plant_list


def simple_list(request, recs, loc_name):
    version = VERSION
    names = {}
    unidentified = []
    for rec in recs:
        plant = rec.plant
        name = plant.longname
        if not name:
            try:
                name = "%s %s" % (plant.upper.latname, name.latname)
            except:
                name = plant.latname
        pnid = plant.pnid
        imid = rec.imid
        if not name in names:
            names[name] = (pnid, [imid])
            if " sp." in name or 'Unidentified' in name:
                print (name)
                unidentified.append(name)
        else:
            names[name][1].append(imid)
    names = names.items()
    names = list(names)
    names.sort()
    print (len(names), "names found")
    generated = timezone.datetime.now()
    return render (request, "photodb/flora.htm", locals())
    ##return HttpResponse(html)
    
