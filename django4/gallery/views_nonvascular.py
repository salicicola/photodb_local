from django.shortcuts import render
import xml.dom.minidom, os, shelve, pickle, datetime, sys, time
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
try:
    from names.models import Name, LegacyName, SpeciesMeta
except:
    print ("should be available in models")
from photodb.models import *
from django.views.decorators.cache import cache_page
from photodb.__init__ import VERSION
    
def index_legacy_simplified(request, template, category='nonvascular', mobile=False):
    print ("simplified ... non vascular", category)
    start = datetime.datetime.now()
    groups = [
        {"name": "Liverworts &#8212; Marchantiophyta", "pnid": 16002 , "fams":[], "species": 0, "published": 0},
        {"name": "Mosses &#8212; Bryophyta", "pnid":11876 , "fams":[], "species": 0, "published": 0},
        {"name": "Brown Algae &#8212; Ochrophyta", "pnid": 16479, "fams":[], "species": 0, "published": 0},
        {"name": "Red Algae &#8212; Rhodophyta", "pnid": 16478, "fams":[], "species": 0, "published": 0},
        {"name": "Green Algae &#8212; Chlorophyta", "pnid": 16477, "fams":[], "species": 0, "published": 0},
        {"name": "Lichens &#8212; Lichenophyta", "pnid": 16476, "fams":[], "species": 0, "published": 0},
        {"name": "Fungi", "pnid": 11998, "fams":[], "species": 0, "published": 0},
    ]
    total_spp = 0
    total_published = 0
    for gr in groups:
        g = Name.objects.get(pnid=gr["pnid"])
        fams = Name.objects.filter(upper = g).order_by('latname')
        for fam in fams:
            fid = fam.pnid
            family = {"latname": fam.latname, "fid": fid, "total_photos": 0, "total_species": 0, "species_pub": 0, "genera":[], "published":0}
            genera = Name.objects.filter(upper = fam).order_by('latname')
            for gen in genera:
                gid = gen.pnid
                genus = {"latname": gen.latname, "fid": fid, "gid": gid, "total_photos": 0, "total_species": 0, "species_pub": 0, "species":[], "published":0}
                species = Name.objects.filter(upper = gen).order_by('latname')
                for spec in species:
                    spid = spec.pnid
                    
                    genus["total_photos"] += 0 ##
                    published_photos = NonVascularImage.objects.filter(plant=spec).filter(nr__gt=0).filter(nr__lt=100).count()
                    spe = {"latname": spec.latname, "fid": fid, "gid": gid, "pnid": spid,
                           "total_photos": 0, "published": published_photos,
                           "colnames": spec.colnames, "authors": spec.authors,
                            "modified": spec.modified.isoformat()[:19]}
                    if published_photos:
                        genus['published'] += published_photos
                        family['published'] += published_photos
                        family["total_species"] += 1
                        gr["published"] += published_photos
                        gr["species"] += 1
                        genus["species"].append(spe)
                if genus["published"]:
                    family["genera"].append(genus)
            if family["published"]:
                gr["fams"].append(family)
        print (gr.get("species"), gr.get("published"))
    ends = datetime.datetime.now()
    delta = ends - start
    print (delta)
    return render(request, template, locals())

def get_table(category):
    if category == 'vascular':
        table = VascularImage
    elif category == 'nonvascular':
        table = NonVascularImage
    elif category == 'animals':
        table = AnimalImage
    else:
        table = VariaImage
    return table    

def get_status(meta):
    if meta.rare:
        if meta.rare == "WL":
            return "Watch Listed"
        elif meta.rare == "H":
            return "Historic"
        elif meta.rare == "SC":
            return "Special Concern"
        elif meta.rare == "T":
            return "Threatened"
        elif meta.rare == "E":
            return "Endangered"
        else:
            return meta.rare ## should never happen
    elif meta.invasive:
        return meta.invasive
    elif meta.introduced:
        return meta.introduced
    else:
        return "Native"

def species_mobile(request, spid, public=True):
    plant = Name.objects.get(pk=int(spid))
    try:
        meta = SpeciesMeta.objects.get(pk=int(spid))
        print ("got meta", meta)
        status = get_status(meta)
    except:
        meta = {}
        status = ""
    if not plant.level == 'species': ## rank
        return HttpResponseBadRequest("mobile version works only at species level")
    genname = plant.upper.latname
    latname = plant.latname
    category = plant.category
    table = get_table(category)
    irecs = table.objects.filter(plant=plant)
    if public:
        irecs = irecs.filter(nr__gt=0).filter(nr__lt=100).order_by('nr')
    else:
        irecs = irecs.order_by('nr')
    print ("finished species mobile for", spid, "got", len(irecs), "photos")
    return render (request, "photodb/thums_species_mobile.htm", locals())


def imgview_mobile(request, spid, imid, public=True):
    plant = Name.objects.get(pk=int(spid))
    genname = plant.upper.latname
    latname = plant.latname
    authors = plant.authors
    comname = plant.colnames
    table = get_table(plant.category)
    irecs = table.objects.filter(plant=plant)
    if public:
        irecs = irecs.filter(nr__gt=0).filter(nr__lt=100).order_by('nr')
    else:
        irecs = irecs.order_by('nr')
    total = len(irecs)    
    for curnum in range(total):
        current = irecs[curnum]
        if current.imid == imid:
            try:
                previmid = irecs[curnum - 1].imid
            except:
                previmid = None
            try:
                nextimid = irecs[curnum + 1].imid
            except:
                nextimid = None
            break
    curnum += 1
    caption = current.caption
    locality = current.location
    date = current.date    
    return render (request, "photodb/imgview_mobile.htm", locals())
