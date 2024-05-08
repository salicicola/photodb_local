import xml.dom.minidom, os, datetime, sys, time
from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from common.models import *
from names.models import *
from photodb.models import *

VERSION = "0.4 alpha (2023-10-28)"
VERSION = "0.5 alpha (2024-01-31)"

def index(request):
    return render(request, 'photodb/flora_index.htm', {'version':VERSION})

def get_names(recs, public=False):
    names = {}
    for rec in recs:
        plant = rec.plant
        if plant in names:
            names[plant.longname]["imids"].append(rec.imid)
        else:
            meta = SpeciesMeta.objects.get(spid=plant.pnid)
            names[plant.longname] = {"upper": plant.upper.upper.upper, "family": plant.upper.upper, "plant": plant, "meta":meta, "imids":[rec.imid]}
        
    return names    


def get_checklist(request, locId="MA.MSF."):
    version = VERSION
    loc_name,  photo_records = loc_name, recs = get_records(locId)
    print (loc_name)
    print (len(photo_records))
    names = get_names(recs, public=False)
    today = "today"
    introduced = 0
    invasive = 0
    for longname in names:
        if names[longname]["meta"].introduced:
            introduced += 1
            if names[longname]["meta"].invasive:
                invasive += 1
    upper = [
        Name.objects.get(pnid=301319),
        Name.objects.get(pnid=301314),
        Name.objects.get(pnid=301309),
        Name.objects.get(pnid=301308),
        Name.objects.get(pnid=301307),
        Name.objects.get(pnid=301299),
    ]
    fams = []
    for longname in names:
        fam = names[longname]["family"]
        if not fam in fams:
            fams.append(fam)
    tree = []
    for upper_pnid in [301319, 301314, 301309, 301308, 301307, 301299]:
        upper = Name.objects.get(pnid=upper_pnid)
        fams = Name.objects.filter(upper=upper)
        tree.append([upper.latname, {"fams": fams}])
    
    print (tree)
    
    return render(request, 'photodb/flora_public.htm', locals())

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
    return simple_list(request, recs, loc_name, locId)

## from flora.plant_list


def simple_list(request, recs, loc_name, locId):
    version = VERSION
    names = {}
    unidentified = []
    published = 0
    for rec in recs:
        plant = rec.plant
        name = plant.longname
        if plant.level == "genus":
            name = "%s sp." % plant.latname
        elif plant.level == "family":
            name = plant.latname
            
        if not name:
            try:
                name = "%s %s" % (plant.upper.latname, name.latname)
            except:
                name = plant.latname
            
        pnid = plant.pnid
        imid = rec.imid
        if rec.nr > 0 and rec.nr < 100:
            is_pub = 1
        else:
            is_pub = 0
        if not name in names:
            if rec.plant.level == 'species':
                syns = rec.plant.name_set.filter(level='synonym') ## to exclude hybrids
                print (syns)
            else:
                syns = []
            ##if syns:
                ##raise Exception("XX")
            names[name] = [pnid, [(imid, rec.nr)], syns, plant, is_pub]
            if " sp." in name or 'Unidentified' in name:
                print (name)
                unidentified.append(name)
        else:
            names[name][1].append((imid, rec.nr))
            names[name][4] += is_pub
    ## get published taxa
    for name in names:
        _recs = names[name][1]
        for _rec in _recs:
            if _rec[1] > 0 and _rec[1] < 100:
                published += 1
                break

    names = names.items()
    names = list(names)
    names.sort()
    print (len(names), "names found")
    generated = timezone.datetime.now()
    return render (request, "photodb/flora.htm", locals())
    ##return HttpResponse(html)
    
